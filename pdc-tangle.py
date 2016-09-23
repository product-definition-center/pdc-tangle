from __future__ import absolute_import
import click
import pdc_client
import asciitree
import itertools
from requests.exceptions import ConnectionError


@click.command()
@click.option('--server', '-s', default='pdc.stg.fedoraproject.org',
              help=('Specifies the FQDN of the PDC instance to connect to.'
                    ' This defaults to pdc.stg.fedoraproject.org.'))
@click.option('--dep_type', '-d', multiple=True,
              default=['RPMBuildRequires', 'RPMRequires'],
              help=('Specifies the dependency types to search for. This can be'
                    ' used more than once. This defaults to RPMBuildRequires'
                    ' and RPMRequires.'))
@click.option('--release', '-r', default='fedora-26',
              help=('Specifies the release to search under.'
                    ' This defaults to fedora-26.'))
@click.argument('artifact')
def cli(artifact, release, dep_type, server):
    """
    The entry point of the tool
    """
    api_url = 'https://{0}/rest_api/v1/'.format(server)
    client = pdc_client.PDCClient(api_url, develop=True)

    try:
        if is_artifact_in_pdc(client, artifact):
            deps_dict = {artifact: {}}
            collect_dependencies(
                client, [artifact], release, dep_type, deps_dict)

            if len(deps_dict.get(artifact)) == 0:
                click.echo(
                    'There are no dependencies for "{}"'.format(artifact))
            else:
                # Print the dependency tree
                tr = asciitree.LeftAligned()
                click.echo(tr({artifact: deps_dict.get(artifact)}))
        else:
            click.echo('"{0}" is not in PDC'.format(artifact))
    except ConnectionError:
        click.echo(
            'The PDC instance "{}" could not be contacted'.format(server))


def collect_dependencies(pdc_obj, artifacts, release, dep_type, deps_dict):
    """
    Updates the deps_dict with the artifacts' recursive dependencies
    :param pdc_obj: an instantiated and configured PDC object
    :param artifacts: a list of artifacts to query for dependencies
    :param release: the release to search under (e.g. fedora-26)
    :param dep_type: the types of dependencies to search for
    (e.g. ['RPMBuildRequires', 'RPMRequires'])
    :param deps_dict: the dictionary keeping track of dependencies. This will
    be updated with the results.
    :return: None
    """

    # Filter down the artifact list to those that have empty dicts in deps_dict
    # This gives us the artifacts that haven't been processed
    artifacts_to_process = [artifact for artifact in artifacts
                            if not deps_dict.get(artifact)]

    # After filtering, check to see if there are any artifacts to process
    if artifacts_to_process:
        dependencies_results = []
        # Query PDC in chunks of 100 for the requested artifacts' dependencies.
        # This is a current workaround due to URI length limitations that
        # was inspired by Ralph Bean <rbean@redhat.com>
        for chunk in chunked_iter(artifacts_to_process, 100):
            dependencies_results = itertools.chain(
                dependencies_results,
                pdc_obj.get_paged(
                    pdc_obj['release-component-relationships/'],
                    from_component_name=chunk,
                    from_component_release=release,
                    type=dep_type,
                    page_size=100
                )
            )

        dependencies_list = []

        for dependency in dependencies_results:
            artifact_name = dependency['from_component']['name']
            dependency_name = dependency['to_component']['name']
            dependencies_list.append(dependency_name)

            add_dependency(artifact_name, dependency_name, deps_dict)

        # Recursively collect all the dependencies' dependencies
        collect_dependencies(pdc_obj, dependencies_list, release, dep_type,
                             deps_dict)


def add_dependency(artifact, new_dependency, deps_dict):
    """
    Adds a dependency to the deps_dict, both in flat and tree format
    :param artifact: the artifact to add the new dependency to
    :param new_dependency: the dependency to add
    :param deps_dict: the dictionary keeping track of dependencies. This will
    be updated with the results.
    :return: None
    """
    if new_dependency not in deps_dict:
        deps_dict.update({new_dependency: {}})

    # If the new dependency relies on the artifact, state that it's circular
    if deps_dict.get(new_dependency).get(artifact):
        deps_dict.get(artifact).update({new_dependency: {
            '<CircularDep on {}>'.format(artifact): {}}})
    # If the artifact relies on itself, state that it's circular
    elif artifact == new_dependency:
        deps_dict.get(artifact).update(
            {'<CircularDep on {}>'.format(artifact): {}})
    else:
        deps_dict.get(artifact).update(
            {new_dependency: deps_dict.get(new_dependency)})


# Function written by Ralph Bean <rbean@redhat.com>
def chunked_iter(iterable, chunk_size):
    """
    Yield successive chunks from an iterable based on the desired chunk size
    Written by Ralph Bean <rbean@redhat.com>
    :param iterable: the iterable that will be chunked out
    :param chunk_size: the amount of items per chunk desired from the iterable
    :return: a generator object containing the next chunk
    """
    for i in range(0, len(iterable), chunk_size):
        yield iterable[i: i + chunk_size]


def is_artifact_in_pdc(pdc_obj, artifact):
    """
    Checks to see if an artifact exists in PDC
    :param pdc_obj: an instantiated and configured PDC object
    :param artifact: the name of the artifact to search for
    :return: a boolean based on if the artifact is in PDC
    """
    results = pdc_obj.get_paged(
        pdc_obj['release-components/'],
        name=artifact
    )

    for item in results:
        if item.get('name') == artifact:
            return True

    return False


if __name__ == '__main__':
    cli()

from typing import Callable
from kfp.components._structures import MetadataSpec
import kfp
import kfp.components as kfplc
from typing import NamedTuple


def artifactmgr(user: str, token: str):
    import json
    from dkube.sdk.api import DkubeApi
    from dkube.sdk.rsrcs import DkubeCode
    from dkube.sdk.rsrcs import DkubeDataset
    from dkube.sdk.rsrcs import DkubeModel


    api = DkubeApi(token=token)

    # Block to create the code resources here
    # Copy/Paste below lines to create N num of code resources from here
    name = "mnist-1"
    code = DkubeCode(user, name=name)
    code.update_git_details(
        'https://github.com/oneconvergence/dkube-examples-internal/tree/2.0.6/tensorflow/classification/mnist/digits/classifier/program')
    api.create_code(code)

    # Create the input dataset resources here
    name = "mnist-ds"
    dataset = DkubeDataset(user, name=name)
    dataset.update_dataset_source(source='git')
    dataset.update_git_details(
        'https://github.com/oneconvergence/dkube-examples-internal/tree/2.0.6/tensorflow/classification/mnist/digits/classifier/data')
    api.create_dataset(dataset)

    # Create the output dataset resources here.
    output_datasets = ["output-ds-1", "output-ds-2"]
    for name in output_datasets:
        dataset = DkubeDataset(user, name=name)
        dataset.update_dataset_source(source='dvs')
        api.create_dataset(dataset)

    # Create the output model resources here
    output_models = ["output-model-1", "output-model-2"]
    for name in output_models:
        model = DkubeModel(user, name=name)
        model.update_model_source(source='dvs')
        api.create_model(model)


def componentize(fn: Callable, name: str, desc: str,
                 image: str, annotations: dict, labels: dict):
    labels.update({'wfid': '{{workflow.uid}}', 'runid': '{{pod.name}}'})
    md = MetadataSpec(annotations=annotations, labels=labels)

    fn._component_human_name = name
    fn._component_description = desc

    cfunc = kfp.components.create_component_from_func(
        fn,
        base_image=image,
    )
    cfunc.component_spec.metadata = md
    envs: Mapping[str, str] = {'pipeline': 'true',
                               'wfid': '{{workflow.uid}}', 'runid': '{{pod.name}}'}
    cfunc.component_spec.implementation.container.env = envs
    cfunc.component_spec.save("artifactmgr.yaml")
    return cfunc


dkube_artifact_op = componentize(artifactmgr,
                                 "dkube_artifactmgr",
                                 "DKube artifact resource manager",
                                 "ocdr/dkube_launcher:viz",
                                 {
                                     'platform': 'Dkube'
                                 },
                                 {
                                     'platform': 'Dkube',
                                     'logger': 'dkubepl',
                                     'dkube.garbagecollect': 'false',
                                     'dkube.garbagecollect.policy':
                                     'all'
                                 })

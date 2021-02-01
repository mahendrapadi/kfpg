import kfp.components as kfplc
from typing import NamedTuple

def visualize(user:str, token:str, run_details: str) -> NamedTuple('Outputs', [
  ('mlpipeline_metrics', 'Metrics'),
]):
    import json
    import pandas as pd
    from minio import Minio
    from dkube.sdk.api import DkubeApi

    print(run_details)
    details = json.loads(run_details)
    jobname = details['Jobname']
    api = DkubeApi(token=token)
    lineage = api.get_training_run_lineage(user, jobname)

    print(lineage)
    model = lineage['run']['parameters']['training']['datums']['outputs'][0]['name']
    version = lineage['run']['parameters']['training']['datums']['outputs'][0]['version']

    model = model.split(':')[1]
    metrics_url = "/users/{}/model/{}/{}/data/metrics/metrics.csv".format(user, model, version)
    print(metrics_url)

    client = Minio(
        "dkube-minio-server.dkube-infra:9000",
        access_key="dkube",
        secret_key="l06dands19s",
        secure=False
    )

    obj = client.get_object(
        "dkube",
        metrics_url,
    )

    metrics = []
    df = pd.read_csv(obj)
    for (name, value) in df.iteritems():
        print(name)
        print(value.values[0])
        metric = {"name": name.strip(), "numberValue": value.values[0]}
        metrics.append(metric)

    metrics = {'metrics': metrics}
    print(metrics)

    return [json.dumps(metrics)]


import kfp
from kfp.components._structures import MetadataSpec
from typing import Callable


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
    cfunc.component_spec.save("metricviz.yaml")
    return cfunc


dkube_metrics_vizop = componentize(visualize,
                                 "dkube_metricsviz",
                                 "Visualizer for dkube metrics",
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

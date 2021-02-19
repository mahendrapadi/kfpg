# How to use MetricVisualizer component
- Check vizpl.py

#metricviz      = components.load_component_from_file("./metricviz.yaml")
#viz            = dkube_metricviz_op(user, auth_token, train.outputs['rundetails'])

#Generate a metrics.csv inside metrics folder of the output

#ALTER TABLE run_metrics MODIFY COLUMN Payload longtext CHARACTER SET latin1;   Ref: https://github.com/kubeflow/pipelines/issues/4304


# How to use artifact manager component
Artifact manager component cna be used to programatically create dkube artifacts from a pipeline
- Check ampl.py

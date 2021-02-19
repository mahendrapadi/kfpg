import kfp.dsl as dsl
from kfp import components
from kubernetes import client as k8s_client
import json

from random import randint

dkube_am_op                 = components.load_component_from_file("./artifactmgr.yaml")

@dsl.pipeline(
    name='dkube-artifactmgr-pl',
    description='sample pipeline to show usage of dkube artifact mgr'
)
def d3pipeline(
    #Dkube user
    user='',
    #Dkube authentication token
    auth_token=''):


    am          = dkube_am_op(user, auth_token)

if __name__ == '__main__':
  import kfp.compiler as compiler
  compiler.Compiler().compile(d3pipeline, __file__ + '.tar.gz')


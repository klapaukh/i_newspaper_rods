from fabric.api import *
from mako.template import Template
import mako
import os
from datetime import datetime
from contextlib import nested

env.run_at="/home/ucgajhe/Scratch/TDA/output"
env.deploy_to="/home/ucgajhe/devel/TDA"
env.clone_url="git@github.com:UCL/i_newspaper_rods.git"
env.corpora="/home/ucgajhe/Scratch/TDA"
env.hosts=['legion.rc.ucl.ac.uk']
env.machine='legion'
env.user='ucgajhe'

modules = nested(prefix('module swap compilers compilers/gnu'),
     prefix('module swap mpi mpi/openmpi/1.10.1/gnu-4.9.2'),
     prefix('module load python2/recommended'))

@task
def cold(branch='master'):
    run('rm -rf '+env.deploy_to)
    run('mkdir -p '+env.deploy_to)
    run('mkdir -p '+env.run_at)
    with cd(env.deploy_to):
        with modules:
                 run('git clone '+env.clone_url)
                 with cd('dataspring'):
                     run('git checkout '+branch)
                     run('python setup.py develop --user')
                     run('py.test')

@task
def warm(branch='master'):
  with cd(os.path.join(env.deploy_to,'dataspring')):
        with modules:
                 run('echo $PYTHONPATH')
                 run('git checkout '+branch)
                 run('git pull')
                 run('python setup.py develop --user')



@task
def test(branch='master'):
  with cd(os.path.join(env.deploy_to,'dataspring')):
        with modules:
             run('py.test')

@task
def sub(query, corpus='TDA',
        subsample=1, processes=4, wall='0:5:0',
        bybook=False):
    env.processes=processes
    env.subsample=subsample
    env.corpus=os.path.join(env.corpora,corpus)
    env.wall=wall
    now=datetime.now()
    stamp=now.strftime("%Y%m%d_%H%M")
    env.outpath=query+'_'+stamp
    template_file_path=os.path.join(os.path.dirname(__file__),env.machine+'.sh.mko')
    script_local_path=os.path.join(os.path.dirname(__file__),env.machine+'.sh')
    config_file_path=os.path.join(os.path.dirname(os.path.dirname(__file__)),'queries',query+'.py')
    env.dest_query='query_'+stamp+'.py'
    with open(template_file_path) as template:
        script=Template(template.read()).render(**env)
        with open(script_local_path,'w') as script_file:
            script_file.write(script)
    with cd(env.run_at):
       put(config_file_path,env.dest_query)
       put(script_local_path,'query.sh')
       run('qsub query.sh')

@task
def repartition(inpath='CompressedALTO64',out='downsample_result',count=64,processes=1, wall='0:15:0', downsample=1):
    env.inpath=os.path.join(env.corpora,inpath)
    env.outpath=os.path.join(env.corpora,out)
    env.processes=processes
    env.wall=wall
    env.count=count
    env.downsample=downsample
    template_file_path=os.path.join(os.path.dirname(__file__),env.machine+'-repartition.sh.mko')
    script_local_path=os.path.join(os.path.dirname(__file__),env.machine+'-repartition.sh')
    with open(template_file_path) as template:
        script=Template(template.read()).render(**env)
        with open(script_local_path,'w') as script_file:
            script_file.write(script)
    with cd(env.run_at):
       put(script_local_path,'repartition.sh')
       run('qsub repartition.sh')
@task
def stat():
    run('qstat')

@task
def fetch():
    with lcd(os.path.join(os.path.dirname(os.path.dirname(__file__)),'results')):
      with cd(env.run_at):
        get('*')

@task
def dependencies():
    with modules:
        run("pip install --user mpi4py")
        run("pip install --user lxml")
        run("pip install --user pyyaml")
        run("pip install --user pytest")

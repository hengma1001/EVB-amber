import os
import yaml
import jinja2
import logging
import subprocess
# from typing_extensions import Annotated

from pathlib import Path
from typing import Type, TypeVar, Optional
from pydantic import validator
from pydantic import BaseModel as _BaseModel
_T = TypeVar("_T")


def read_evbout(evb_out) -> list: 
    label = os.path.basename(os.path.dirname(evb_out))
    df = []
    with open(evb_out, 'r') as f: 
        for step in f.read().split('{NSTEP}')[1:]:
            step = step.split()
            if len(step) < 16:
                break
            local_cell = {
                'label': label,
                'step': step[1], 
                'time': step[3], 
                'H11': step[6], 
                'H12': step[7],
                'H22': step[9],
                'vec_0': step[12], 
                'vec_1': step[13],
                'RC': step[-1]
            }
            df.append(local_cell)
    return df


def build_logger(debug=0):
    logger_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=logger_level, format='%(asctime)s %(message)s')
    logger = logging.getLogger(__name__)
    return logger

def run_and_save(command: str, log):
    tsk = subprocess.Popen(
            command,
            stdout=log, # subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True)
    tsk.wait()

def render_jj_template(
        jj_env: jinja2.environment, 
        template_name: str, 
        render_dict: dict, 
        out_file: Path): 
    template = jj_env.get_template(template_name)
    scripts = template.render(render_dict)
    with open(out_file, 'w') as f: 
        f.write(scripts)

class BaseModel(_BaseModel):
    def dump_yaml(self, cfg_path: Path):
        with open(cfg_path, 'w') as fp:
            yaml.dump(self.to_dict(), fp, indent=4, sort_keys=False)

    @classmethod
    def from_yaml(cls: Type[_T], filename: Path) -> _T:
        with open(filename, 'r') as fp:
            raw_data = yaml.safe_load(fp)
        return cls(**raw_data)

def to_abspath(filepath: Path): 
    return filepath.absolute() 

class md_cfg(BaseModel): 
    pdb : Path # Annotated[Path, Field(default_factory=os.path.abspath)]
    top : Path
    rst : Optional[Path] = None
    evb : Optional[Path] = None

    # validator
    @validator('pdb', 'top', 'rst', 'evb')
    def to_abspath(cls, v): 
        if v: 
            return v.resolve()

class grp_cfg(BaseModel):
    mr_cfg : md_cfg
    mp_cfg : md_cfg
    n_steps : int = 20
    temperature : float = 300. 

class evb_cfg(BaseModel):
    rc_min: float
    rc_max: float
    rc_inc: float
    iatom : int # i-k bond in mr
    jatom : int # j-k bond in mp
    katom : int
    spring_const : float
    xcnst : float

class evb_md_cfg(BaseModel): 
    mpi_exe: Optional[str]
    sander_exe: Optional[str]
    grp_cfg : Optional[grp_cfg]
    evb_cfg : Optional[evb_cfg]


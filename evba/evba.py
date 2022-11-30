import os
import jinja2
import numpy as np
from pathlib import Path
from typing import Optional

from utils import build_logger, evb_md_cfg


logger = build_logger()


class EVBA(object): 
    """
    """
    def __init__(self, 
        cfg_file : Path,
        ) -> None:
        self.cfg = evb_md_cfg().from_yaml(cfg_file)

    def setup_evb(self) -> None:
        """
        write the input files for evb runs
        """
        jj_env = jinja2.Environment(
            loader=jinja2.PackageLoader("evba"),
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=False,
        )

        mdin_amber = jj_env.get_template("mdin.j2")
        scripts = mdin_amber.render(
            {'grp_cfg': self.cfg.grp_cfg
            }
            )
        with open('mdin', 'w') as f: 
            f.write(scripts)

        # evb_grp = jj_env.get_template('evb_grp.j2')
        # scripts = mdin_amber.render(
        #     {'n_steps': self.md_cfg.n_steps, 
        #     'temperature': self.md_cfg.temperature,
        #     }
        #     )
        # with open('evb_grp', 'w') as f: 
        #     f.write(scripts)



if __name__ == '__main__': 
    yml = '../examples/test.yml' 
    evba_run = EVBA(yml)
    print(evba_run.cfg)
    evba_run.setup_evb()

    

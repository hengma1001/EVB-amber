import os
import jinja2
import numpy as np
from pathlib import Path
from typing import Optional

from utils import build_logger, evb_md_cfg
from utils import render_jj_template


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

        mdin_path = os.path.abspath('mdin')
        render_jj_template(jj_env, 'mdin.j2', 
                {'grp_cfg': self.cfg.grp_cfg}, mdin_path)

        rc_min, rc_max = self.cfg.evb_cfg.rc_min, self.cfg.evb_cfg.rc_max
        rc_inc  = self.cfg.evb_cfg.rc_inc
        rc_list = np.arange(rc_min, rc_max+rc_inc, rc_inc)

        for i, rc0 in enumerate(rc_list): 
            save_path = f"evb_{i:03}_rc_{rc0:.2f}"
            os.makedirs(save_path)

            mr_evb = os.path.abspath(f"{save_path}/mr_evb")
            render_jj_template(jj_env, 'mr_evb.j2', 
                    {'evb': self.cfg.evb_cfg, 'rc0': rc0}, 
                    mr_evb
                    )

            mp_evb = os.path.abspath(f"{save_path}/mp_evb")
            render_jj_template(jj_env, 'mp_evb.j2', 
                    {'evb': self.cfg.evb_cfg, 'rc0': rc0}, 
                    mp_evb
                    )
            self.cfg.grp_cfg.mr_cfg.evb = mr_evb
            self.cfg.grp_cfg.mp_cfg.evb = mp_evb
            grp_file = os.path.abspath(f"{save_path}/grp_evb")
            render_jj_template(jj_env, 'evb_grp.j2', 
                    {'mdin': mdin_path, 'mr': self.cfg.grp_cfg.mr_cfg, 
                    'mp': self.cfg.grp_cfg.mp_cfg}, 
                    grp_file)
            

        # mr_evb = jj_env.get_template('mr_evb')
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

    

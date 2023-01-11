import os
import jinja2
import subprocess
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Optional

from .utils import build_logger, evb_md_cfg
from .utils import render_jj_template, read_evbout


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
        K_k = self.cfg.evb_cfg.spring_const 
        # [600 + 2000*abs(rc0**2 - 0.3) for rc0 in rc_list]
        # K_k = [400 for rc0 in rc_list]

        evb_df = []
        for i, rc0 in enumerate(rc_list[::]): 
            save_path = f"evb_{i:03}_rc_{rc0:.2f}"
            os.makedirs(save_path)

            const_spring = K_k # [i]
            mr_evb = os.path.abspath(f"{save_path}/mr_evb")
            render_jj_template(jj_env, 'mr_evb.j2', 
                    {'evb': self.cfg.evb_cfg, 'rc0': rc0, 
                    'const_spring': const_spring}, 
                    mr_evb,
                    )

            mp_evb = os.path.abspath(f"{save_path}/mp_evb")
            render_jj_template(jj_env, 'mp_evb.j2', 
                    {'evb': self.cfg.evb_cfg, 'rc0': rc0, 
                    'const_spring': const_spring}, 
                    mp_evb
                    )
            self.cfg.grp_cfg.mr_cfg.evb = mr_evb
            self.cfg.grp_cfg.mp_cfg.evb = mp_evb
            grp_file = os.path.abspath(f"{save_path}/grp_evb")
            render_jj_template(jj_env, 'evb_grp.j2', 
                    {'mdin': mdin_path, 'mr': self.cfg.grp_cfg.mr_cfg, 
                    'mp': self.cfg.grp_cfg.mp_cfg}, 
                    grp_file)

            run_cmd = f"{self.cfg.mpi_exe} -n 2 {self.cfg.sander_exe} -ng 2 -groupfile {grp_file}"
            run_log = os.path.abspath(f"{save_path}/run_log")
            process = subprocess.Popen(
                run_cmd,
                shell=True,
                cwd=save_path,
                stdout=open(run_log, 'w'),
                stderr=subprocess.STDOUT,
                preexec_fn=os.setsid
            )
            process.wait()
            logger.info(f"Finished RC at {rc0:.2f}. ")

            # evb_out = 
            evb_out = read_evbout(os.path.abspath(f'{save_path}/evbout'))
            evb_df += evb_out

        evb_df = pd.DataFrame(evb_df)
        evb_df.to_pickle('evb.pkl')


if __name__ == '__main__': 
    yml = '../examples/test.yml' 
    evba_run = EVBA(yml)
    print(evba_run.cfg)
    evba_run.setup_evb()

    

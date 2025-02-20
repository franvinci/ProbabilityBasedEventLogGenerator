import os
os.chdir('SIMOD_TEST')

import simod

from pathlib import Path

from simod.settings.simod_settings import SimodSettings
from simod.simod import Simod
from simod.event_log.event_log import EventLog

# case_studies = ['purchasing', 'acr', 'cvs', 'bpi12', 'bpi17', 'bac', 'production']
case_studies = ['production']


if __name__ == "__main__":

    for case_study in case_studies:

        configuration = Path(case_study+'/'+'complete_configuration.yml')
        settings = SimodSettings.from_path(configuration)

        output = Path(case_study+'/'+'output')

        event_log = EventLog.from_path(
            log_ids=settings.common.log_ids,
            train_log_path=settings.common.train_log_path,
            test_log_path=settings.common.test_log_path,
            preprocessing_settings=settings.preprocessing,
            need_test_partition=settings.common.perform_final_evaluation,
        )

        simod = Simod(settings, event_log=event_log, output_dir=output)
        simod.run()
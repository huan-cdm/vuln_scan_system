import json
import os
from app import utils
from app.config import Config

logger = utils.get_logger()

class FetchDomain():
    def __init__(self, domain, brute_dict_path, mode, subfinder_bin = None, tmp_dir = None):
        self.domain = domain
        self.brute_dict_path = brute_dict_path
        self.mode = mode
        self.tmp_dir = tmp_dir
        self.output_path = os.path.join(self.tmp_dir,
                                        "subfinder_{}".format(utils.random_choices()))

        self.subfinder_bin = subfinder_bin

        self.cmd = self._build_cmd()


    def _build_cmd(self):
        test_source = "hackertarget"

        if self.mode == 'test':
            sources = ["--sources {}".format(test_source)]
        else:
            sources = [
                "--exclude-sources dnsdb,threatcrowd,googleter,dnsdumpster,waybackarchive,archiveis,ask,netcraft"]


        cmd = [self.subfinder_bin,
               "-b",
               "-t 10",
               "-w {}".format(self.brute_dict_path),
               "-oT",
               "-nW",
               "-o {}".format(self.output_path),
               "-d {}".format(self.domain)]

        cmd.extend(sources)

        return cmd

    '''domain_dict
    {
        "www.freebuf.com": "39.96.250.248"
    } 
    '''
    def _get_result(self):
        with open(self.output_path, encoding='utf-8') as f:
            domain_dict = json.load(f)
            return domain_dict

    def _delete_output_path(self):
        try:
            os.unlink(self.output_path)
        except Exception as e:
            logger.warning(e)

    def run(self):
        utils.exec_system(self.cmd)

        domain_dict = self._get_result()

        self._delete_output_path()

        return domain_dict


def fetch_domain(domain, brute_dict_path, mode):
    try:
        return FetchDomain(domain, brute_dict_path, mode,
                           subfinder_bin = Config.SUBFINDER_BIN, tmp_dir = Config.TMP_PATH).run()
    except Exception as e:
        logger.exception(e)
        return {}



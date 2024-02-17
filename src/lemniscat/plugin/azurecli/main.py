
import argparse
import ast
import logging
import os
import re
from logging import Logger
from lemniscat.core.contract.engine_contract import PluginCore
from lemniscat.core.model.models import Meta, TaskResult
from lemniscat.core.util.helpers import FileSystem, LogUtil

from lemniscat.plugin.azurecli.azurecli import AzureCli

_REGEX_CAPTURE_VARIABLE = r"(?:\${{(?P<var>[^}]+)}})"

class Action(PluginCore):

    def __init__(self, logger: Logger) -> None:
        super().__init__(logger)
        plugin_def_path = os.path.abspath(os.path.dirname(__file__)) + '/plugin.yaml'
        manifest_data = FileSystem.load_configuration_path(plugin_def_path)
        self.meta = Meta(
            name=manifest_data['name'],
            description=manifest_data['description'],
            version=manifest_data['version']
        )
        
    def __interpret(self, script: str, variables: dict) -> str:
        if(script is None):
            return None
        if(isinstance(script, str)):
            matches = re.findall(_REGEX_CAPTURE_VARIABLE, script)
            if(len(matches) > 0):
                for match in matches:
                    var = str.strip(match)
                    if(var in variables):
                        script = script.replace(f'${{{{{match}}}}}', variables[var])
                        self._logger.debug(f"Interpreting variable: {var} -> {variables[var]}")
                    else:
                        script = script.replace(f'${{{{{match}}}}}', "")
                        self._logger.debug(f"Variable not found: {var}. Replaced by empty string.")
        return script    

    def __run_azurecli(self, parameters: dict = {}, variables: dict = {}) -> TaskResult:
        # launch azurecli command
        cli = AzureCli()
        result = {}
        if(parameters['commandtype'] == 'inline'):
            script = self.__interpret(parameters['script'], variables)
            self._logger.debug("---------------------------")
            self._logger.debug("Interpreted script: ")
            script = script.replace("'", "\"")
            self._logger.debug(f"{script}")
            self._logger.debug("---------------------------")
            result = cli.run(parameters['scripttype'], script)
        elif(parameters['commandtype'] == 'file'):
            if(parameters.get('fileParams')) is not None:
                params = parameters['fileParams']
                args = []
                for param in params:
                    args.append(f'-{param}')
                    args.append(self.__interpret(params[param], variables))
                result = cli.run_script_with_args(parameters['scripttype'], parameters['filePath'], args)
            else:    
                result= cli.run_script(parameters['scripttype'], parameters['filePath'])
        
        if(result[3] is not None):   
            super().appendVariables(result[3])  
                
        if(result[0] != 0):
            return TaskResult(
                name=f'AzureCli run',
                status='Failed',
                errors=result[2])
        else:
            return TaskResult(
                name='AzureCli run',
                status='Completed',
                errors=[0x0000]
        )
        

    def invoke(self, parameters: dict = {}, variables: dict = {}) -> TaskResult:
        self._logger.debug(f'Run AzureCli with {parameters["scripttype"]} -> {self.meta}')
        task = self.__run_azurecli(parameters, variables)
        return task
    
    def test_logger(self) -> None:
        self._logger.debug('Debug message')
        self._logger.info('Info message')
        self._logger.warning('Warning message')
        self._logger.error('Error message')
        self._logger.critical('Critical message')

def __init_cli() -> argparse:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-p', '--parameters', required=True, 
        help="""(Required) Supply a dictionary of parameters which should be used. The default is {}
        """
    )
    parser.add_argument(
        '-v', '--variables', required=True, help="""(Optional) Supply a dictionary of variables which should be used. The default is {}
        """
    )                
    return parser
        
if __name__ == "__main__":
    logger = LogUtil.create()
    action = Action(logger)
    __cli_args = __init_cli().parse_args()   
    action.invoke(ast.literal_eval(__cli_args.parameters), ast.literal_eval(__cli_args.variables))
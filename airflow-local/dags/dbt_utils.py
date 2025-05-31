from airflow.models import BaseOperator
from airflow.hooks.base import BaseHook
from airflow.operators.bash import BashOperator
from typing import Optional, List
import yaml
import os

# Default dbt working directory - moved outside dags folder for write permissions
DEFAULT_DBT_DIR = "/opt/airflow/dbt"

class DbtBaseOperator(BashOperator):
    """
    Base class for all dbt operators that handles directory management.
    Each dbt command will be executed in the specified dbt_dir.
    
    :param dbt_dir: Directory where dbt project lives
    :param dbt_command: The dbt command to execute (e.g. 'run', 'test')
    :param select: Optional selector for dbt models
    :param command_args: Additional command line arguments
    """
    
    template_fields = ('select', 'dbt_dir')
    
    def __init__(
        self,
        dbt_command: str,
        dbt_dir: str = DEFAULT_DBT_DIR,
        select: Optional[str] = None,
        command_args: Optional[List[str]] = None,
        **kwargs
    ) -> None:
        self.dbt_dir = dbt_dir
        
        # Build the dbt command
        cmd_parts = [f'cd {dbt_dir}', '&&', 'dbt', dbt_command]
        
        # Add select if specified
        if select:
            cmd_parts.extend(['--select', select])
            
        # Add any additional arguments
        if command_args:
            cmd_parts.extend(command_args)
            
        super().__init__(
            bash_command=' '.join(cmd_parts),
            **kwargs
        )

class DbtGenerateProfilesOperator(BaseOperator):
    """
    Operator that generates a dbt profiles.yml file from an Airflow connection.
    
    :param connection_id: The Airflow connection ID to use for database configuration
    :param profiles_dir: Directory where profiles.yml should be created
    :param target: The dbt target profile to use (default: dev)
    :param profile_name: Name of the dbt profile (default: default)
    """
    
    template_fields = ('connection_id', 'profiles_dir', 'target')
    
    def __init__(
        self,
        connection_id: str,
        profiles_dir: str = DEFAULT_DBT_DIR,
        target: str = 'dev',
        profile_name: str = 'default',
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.connection_id = connection_id
        self.profiles_dir = profiles_dir
        self.target = target
        self.profile_name = profile_name
    
    def execute(self, context):
        # Get connection details from Airflow
        conn = BaseHook.get_connection(self.connection_id)
        
        # Create profiles directory if it doesn't exist
        os.makedirs(self.profiles_dir, exist_ok=True)
        
        # Build the profiles configuration
        profiles_config = {
            self.profile_name: {
                'outputs': {
                    self.target: {
                        'type': 'postgres',  # Assuming Postgres, adjust if needed
                        'host': conn.host,
                        'port': conn.port,
                        'user': conn.login,
                        'password': conn.password,
                        'dbname': conn.schema,
                        'schema': 'dbt',  # Default schema for dbt
                        'threads': 4
                    }
                },
                'target': self.target
            }
        }
        
        # Write the profiles.yml file
        profiles_path = os.path.join(self.profiles_dir, 'profiles.yml')
        with open(profiles_path, 'w') as f:
            yaml.dump(profiles_config, f, default_flow_style=False)
        
        self.log.info(f"Generated dbt profiles.yml at {profiles_path}")
        return profiles_path

class DbtRunOperator(DbtBaseOperator):
    """
    Operator that executes 'dbt run' command.
    
    Example usage:
    ```python
    dbt_run = DbtRunOperator(
        task_id='dbt_run',
        select='my_model+'  # Optional: run specific model(s)
    )
    ```
    """
    def __init__(
        self,
        select: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(
            dbt_command='run',
            select=select,
            **kwargs
        )

class DbtTestOperator(DbtBaseOperator):
    """
    Operator that executes 'dbt test' command.
    
    Example usage:
    ```python
    dbt_test = DbtTestOperator(
        task_id='dbt_test',
        select='my_model+'  # Optional: test specific model(s)
    )
    ```
    """
    def __init__(
        self,
        select: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(
            dbt_command='test',
            select=select,
            **kwargs
        )

class DbtBuildOperator(DbtBaseOperator):
    """
    Operator that executes 'dbt build' command.
    
    Example usage:
    ```python
    dbt_build = DbtBuildOperator(
        task_id='dbt_build',
        select='my_model+'  # Optional: build specific model(s)
    )
    ```
    """
    def __init__(
        self,
        select: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(
            dbt_command='build',
            select=select,
            **kwargs
        )

class DbtSeedOperator(DbtBaseOperator):
    """
    Operator that executes 'dbt seed' command.
    
    Example usage:
    ```python
    dbt_seed = DbtSeedOperator(
        task_id='dbt_seed',
        select='my_seed+'  # Optional: load specific seed(s)
    )
    ```
    """
    def __init__(
        self,
        select: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(
            dbt_command='seed',
            select=select,
            **kwargs
        )

class DbtDocsGenerateOperator(DbtBaseOperator):
    """
    Operator that executes 'dbt docs generate' command.
    
    Example usage:
    ```python
    dbt_docs = DbtDocsGenerateOperator(
        task_id='dbt_docs'
    )
    ```
    """
    def __init__(self, **kwargs) -> None:
        super().__init__(
            dbt_command='docs generate',
            **kwargs
        )

class DbtDebugOperator(DbtBaseOperator):
    """
    Operator that executes 'dbt debug' command to validate your dbt project configuration.
    
    Example usage:
    ```python
    dbt_debug = DbtDebugOperator(
        task_id='dbt_debug',
        config=True  # Optional: show all config info
    )
    ```
    """
    def __init__(
        self,
        config: bool = False,
        **kwargs
    ) -> None:
        command_args = ['--config'] if config else None
        super().__init__(
            dbt_command='debug',
            command_args=command_args,
            **kwargs
        )

class DbtCompileOperator(DbtBaseOperator):
    """
    Operator that executes 'dbt compile' command to compile your dbt project.
    
    Example usage:
    ```python
    dbt_compile = DbtCompileOperator(
        task_id='dbt_compile',
        select='my_model+'  # Optional: compile specific model(s)
    )
    ```
    """
    def __init__(
        self,
        select: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(
            dbt_command='compile',
            select=select,
            **kwargs
        )
# Standard library imports
import json
import logging
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence

# Third-party imports
import cbsodata
import pandas as pd
import requests
from sqlalchemy import create_engine

# Airflow imports
from airflow.hooks.base import BaseHook
from airflow.models.baseoperator import BaseOperator
from airflow.datasets import Dataset

# Create a module-specific logger
logger = logging.getLogger(__name__)
# logger.propagate = False  # Prevent propagation to parent loggers
if not logger.handlers:  # Only add handler if none exists
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('[%(asctime)s - %(levelname)s]: %(message)s'))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

@dataclass
class CBSTable:

    updated: str
    id: str
    identifier: str
    title: str
    short_title: str
    short_description: str
    summary: str
    modified: str
    meta_data_modified: str
    reason_delivery: str
    explanatory_text: str
    output_status: str
    source: str
    language: str
    catalog: str
    frequency: str
    period: str
    summary_and_links: str
    api_url: str
    feed_url: str
    default_presentation: str
    default_selection: str
    graph_types: str
    record_count: str
    column_count: str
    search_priority: str

def to_snake_case(name: str) -> str:
    """Convert a camelCase or CamelCase string to snake_case.
    
    Args:
        name: The string to convert
        
    Returns:
        The converted snake_case string
    """
    # Handle empty string
    if not name:
        return name
    
    if name.upper() == name:
        return name.lower()

    words = []

    current_word = ""
    for char in name:
        if char.lower() != char:
            if current_word != "":
                words.append(current_word)
            current_word = ""

        current_word += char        

    words.append(current_word)
    return "_".join(words).lower()

def get_all_tables() -> list[CBSTable]:
    raw_tables = cbsodata.get_table_list()
    tables = []
    for table in raw_tables:
        renamed_dict = {to_snake_case(key): value for key,
        value in table.items()}
        table = CBSTable(**renamed_dict)
        tables.append(table)
    return tables

def search_for_table(tables, search_term):
    for table in tables: 
        if search_term.lower() in table.short_description.lower():
            yield table
        if search_term.lower() in table.summary.lower():    
            yield table
        if search_term.lower() in table.title.lower():
            yield table
        if search_term.lower() in table.short_title.lower():
            yield table 
    return None

def table_name_from_short_title(table: CBSTable) -> str:
    result = ''.join(c if c.isalnum() else '_' for c in table.short_title.lower())
    return result.strip('_') + "_" + str(table.id)

def list_tables(search_term: str) -> list[dict]:
    tables = get_all_tables()
    logger.info(f"Found {len(tables)} tables.")

    result_tables = []
    tables = list(search_for_table(tables, search_term))  # Convert generator to list
    logger.info(f"Searching for keyword: {search_term}, found {len(tables)} tables.")
    if not tables:
        logger.info("No tables found matching 'politie'")
    else:
        for table in tables:
            shorter_desc = table.short_description[0:29].strip().replace('\n', ' ')
            table_new_name = table_name_from_short_title(table)
            logger.info(f"\t{table_new_name}:  {shorter_desc}...")

            result_tables.append({
                "table_id": table.identifier, 
                "table_name": table_new_name, 
                "table_description": shorter_desc
            })
    
    return result_tables

class ListPoliceTables(BaseOperator):
    """
    Operator that searches for police-related tables in CBS Open Data
    and returns their metadata as a list of dictionaries.
    """
    
    def __init__(
        self,
        search_term: str = "politie",
        limit=100000,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.search_term = search_term
        self.limit = limit

    def execute(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Execute the operator to search for and list police-related tables.
        
        Returns:
            List of dictionaries containing table metadata (id, name, description)
        """
        results = list_tables(self.search_term)[:self.limit]
        logger.info(f"Found {len(results)} tables matching '{self.search_term}', returning up to {self.limit} results")
        return results

class DocumentationOperator(BaseOperator):
    """
    Operator that prints the documentation string of a Python object.
    """

    def __init__(
        self,
        object_name: str,
        **kwargs
    ) -> None:
        """
        Initialize the operator.
        
        Args:
            object_name: Name of the Python object whose documentation to print
        """
        super().__init__(**kwargs)
        self.object_name = object_name

    def execute(self, context: Dict[str, Any]) -> str:
        """
        Execute the operator to print an object's documentation.
        
        Returns:
            The documentation string of the specified object
        """
        # Get the object from this module
        obj = globals().get(self.object_name)
        
        if obj is None:
            raise ValueError(f"Object {self.object_name} not found in module")
            
        if not hasattr(obj, '__doc__') or obj.__doc__ is None:
            logger.warning(f"No documentation found for {self.object_name}")
            return ""
            
        doc = obj.__doc__.strip()
        logger.info(f"Documentation for {self.object_name}:\n{doc}")
        return doc

class DbtRunOperator(BaseOperator):
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
    template_fields = ('select',)
    
    def __init__(
        self,
        select: Optional[str] = None,
        **kwargs
    ) -> None:
        """Initialize the operator."""
        super().__init__(**kwargs)
        self.select = select

    def execute(self, context: Dict[str, Any]) -> None:
        """Execute dbt run command."""
        cmd = ['dbt', 'run']
        if self.select:
            cmd.extend(['--select', self.select])
        logger.info(f"Executing: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info(result.stdout)
        if result.stderr:
            logger.warning(result.stderr)

class DbtTestOperator(BaseOperator):
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
    template_fields = ('select',)
    
    def __init__(
        self,
        select: Optional[str] = None,
        **kwargs
    ) -> None:
        """Initialize the operator."""
        super().__init__(**kwargs)
        self.select = select

    def execute(self, context: Dict[str, Any]) -> None:
        """Execute dbt test command."""
        cmd = ['dbt', 'test']
        if self.select:
            cmd.extend(['--select', self.select])
        logger.info(f"Executing: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info(result.stdout)
        if result.stderr:
            logger.warning(result.stderr)

class DbtBuildOperator(BaseOperator):
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
    template_fields = ('select',)
    
    def __init__(
        self,
        select: Optional[str] = None,
        **kwargs
    ) -> None:
        """Initialize the operator."""
        super().__init__(**kwargs)
        self.select = select

    def execute(self, context: Dict[str, Any]) -> None:
        """Execute dbt build command."""
        cmd = ['dbt', 'build']
        if self.select:
            cmd.extend(['--select', self.select])
        logger.info(f"Executing: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info(result.stdout)
        if result.stderr:
            logger.warning(result.stderr)

class DbtSeedOperator(BaseOperator):
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
    template_fields = ('select',)
    
    def __init__(
        self,
        select: Optional[str] = None,
        **kwargs
    ) -> None:
        """Initialize the operator."""
        super().__init__(**kwargs)
        self.select = select

    def execute(self, context: Dict[str, Any]) -> None:
        """Execute dbt seed command."""
        cmd = ['dbt', 'seed']
        if self.select:
            cmd.extend(['--select', self.select])
        logger.info(f"Executing: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info(result.stdout)
        if result.stderr:
            logger.warning(result.stderr)

class DbtDocsGenerateOperator(BaseOperator):
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
        """Initialize the operator."""
        super().__init__(**kwargs)

    def execute(self, context: Dict[str, Any]) -> None:
        """Execute dbt docs generate command."""
        cmd = ['dbt', 'docs', 'generate']
        logger.info(f"Executing: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info(result.stdout)
        if result.stderr:
            logger.warning(result.stderr)

class ProcessPoliceTable(BaseOperator):
    """
    Operator that processes a single police-related table from CBS Open Data.
    Can be used either directly with a table name or with dynamic task mapping in Airflow.

    Two ways to use this operator:

    1. Direct instantiation with table name:
    ```python
    process_table = ProcessPoliceTable(
        task_id='process_budget',
        table_name='police_budget'
    )
    ```

    2. With dynamic task mapping:
    ```python
    list_tables = ListPoliceTables(
        task_id='list_police_tables',
        search_term='politie'
    )

    process_tables = ProcessPoliceTable.partial(
        task_id='process_table'  # Base task_id, Airflow will append numbers
    ).expand(
        table_data=list_tables.output
    )

    list_tables >> process_tables
    ```
    """
    
    template_fields = ('table_data', 'table_name')
    
    def __init__(
        self,
        table_name: Optional[str] = None,
        table_data: Optional[Dict[str, Any]] = None,  # This will be expanded by Airflow
        **kwargs
    ) -> None:
        """
        Initialize the operator.
        
        Args:
            table_name: Name of the table to process (for direct instantiation)
            table_data: Dictionary containing the table metadata to process (for dynamic mapping)
        """
        super().__init__(**kwargs)
        
        if table_name is None and table_data is None:
            raise ValueError("Either table_name or table_data must be provided")
        
        self.table_name = table_name
        self.table_data = table_data

    def _get_table_info(self) -> Dict[str, str]:
        """Get table ID and name either from table_data or by searching."""
        if self.table_data is not None:
            return {
                'table_id': self.table_data['table_id'],
                'table_name': self.table_data['table_name']
            }
        
        tables = list_tables("politie")
        matching_tables = [t for t in tables if t['table_name'] == self.table_name]
        if not matching_tables:
            raise ValueError(f"No table found with name {self.table_name}")
            
        return {
            'table_id': matching_tables[0]['table_id'],
            'table_name': self.table_name
        }

    def _fetch_table_data(self, table_id: str) -> List[Dict[str, Any]]:
        """Fetch data from CBS API for given table ID."""
        return cbsodata.get_data(table_id)

    def _prepare_result_metadata(self, table_info: Dict[str, str], data: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare metadata about the processed table."""
        return {
            'table_metadata': self.table_data if self.table_data else {
                'table_name': table_info['table_name'], 
                'table_id': table_info['table_id']
            },
            'row_count': len(data),
            'processed_at': context['ts'],
            'processed_by': context['task_instance'].task_id
        }

    def _save_data_to_file(self, table_name: str, data: List[Dict[str, Any]]) -> str:
        """Save table data to JSON file and return the filename."""
        data_dir = "data"
        os.makedirs(data_dir, exist_ok=True)
        
        filename = os.path.join(data_dir, f"{table_name}.json")
        
        with open(filename, 'w') as f:
            json.dump(data, f)
            
        data = json.load(f)
        print(pd.DataFrame(data).head())
        
        return filename

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the operator to process a single table.
        
        Returns:
            Dictionary containing the processed data for this specific table
        """
        # Get table information
        table_info = self._get_table_info()
        logger.info(f"Processing table: {table_info['table_name']}")
        
        # Fetch and process the data
        table_data = self._fetch_table_data(table_info['table_id'])
        
        # Prepare result metadata
        result = self._prepare_result_metadata(table_info, table_data, context)
        
        # Save data to file
        filename = self._save_data_to_file(table_info['table_name'], table_data)
        result['data_file'] = filename
        
        logger.info(f"Processed {result['row_count']} rows from table {table_info['table_name']}")
        return result

class UploadToDWHOperator(BaseOperator):
    """
    Operator that uploads JSON files to a data warehouse using a configured connection.
    Can handle either a single file path or a list of file paths passed via XCom.

    Args:
        task_id: Unique task identifier
        connection_id: Name of the Airflow connection to use for database access
        file_path: Optional direct file path to upload
        xcom_task_id: Optional task ID to pull file path(s) from via XCom
        xcom_key: Optional XCom key to use when pulling file path(s)
        **kwargs: Additional arguments to pass to BaseOperator
    """

    template_fields = ('file_path',)

    def __init__(
        self,
        connection_id: str,
        file_path: Optional[str] = None,
        xcom_task_id: Optional[str] = None,
        xcom_key: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.connection_id = connection_id
        self.file_path = file_path
        self.xcom_task_id = xcom_task_id
        self.xcom_key = xcom_key

    def _get_engine(self):
        """Create SQLAlchemy engine from connection details"""
        conn = BaseHook.get_connection(self.connection_id)
        # Ensure we're using postgresql:// instead of postgres://
        uri = conn.get_uri().replace('postgres://', 'postgresql://')
        return create_engine(uri)

    def _get_files_to_process(self, context) -> List[str]:
        """Determine which files to process from direct path or XCom"""
        if self.file_path:
            return [self.file_path]
        
        if self.xcom_task_id:
            xcom_value = context['task_instance'].xcom_pull(
                task_ids=self.xcom_task_id,
                key=self.xcom_key
            )
            if isinstance(xcom_value, list):
                return xcom_value
            return [xcom_value]
            
        raise ValueError("No files specified for upload")

    def _load_json_to_df(self, file_path: str | Dataset) -> pd.DataFrame:
        """Load JSON file into pandas DataFrame"""
        # Handle Dataset objects by extracting their uri
        if isinstance(file_path, Dataset):
            file_path = file_path.uri
        
        with open(file_path, 'r') as f:
            data = json.load(f)
        return pd.DataFrame(data)

    def _get_table_name(self, file_path: str | Dataset) -> str:
        """Generate table name from file path"""
        # Handle Dataset objects by extracting their uri
        if isinstance(file_path, Dataset):
            file_path = file_path.uri
            
        return os.path.splitext(os.path.basename(file_path))[0].lower()

    def _upload_df_to_db(self, df: pd.DataFrame, table_name: str, engine) -> int:
        """Upload DataFrame to database table"""
        print(df.head())
        df.to_sql(
            name=table_name,
            con=engine,
            if_exists='replace',
            index=False
        )
        return len(df)

    def _process_single_file(self, file_path: str, engine) -> Dict[str, Any]:
        """Process a single file and upload to database"""
        print(f"Processing file: {file_path}")
        self.log.info(f"Processing file: {file_path}")
        
        df = self._load_json_to_df(file_path)
        table_name = self._get_table_name(file_path)
        rows_uploaded = self._upload_df_to_db(df, table_name, engine)
        
        self.log.info(f"Uploaded {rows_uploaded} rows to table {table_name}")
        
        return {
            'file': file_path,
            'table': table_name,
            'rows': rows_uploaded
        }

    def execute(self, context) -> List[Dict[str, Any]]:
        """
        Executes the upload operation by:
        1. Getting file path(s) either directly or from XCom
        2. Reading JSON data from the file(s)
        3. Uploading to the configured database connection
        """
        engine = self._get_engine()
        files_to_process = self._get_files_to_process(context)
        
        return [
            self._process_single_file(file_path, engine)
            for file_path in files_to_process
        ]

class ListDWHTables(BaseOperator):
    """
    Operator that lists tables in the data warehouse using the specified connection.

    Example usage:
    ```python
    list_tables = ListDWHTables(
        task_id='list_dwh_tables',
        connection_id='dwh',
        schema='public'  # Optional schema name
    )
    ```
    """

    template_fields = ('schema',)

    def __init__(
        self,
        connection_id: str,
        schema: Optional[str] = None,
        **kwargs
    ) -> None:
        """Initialize the operator."""
        super().__init__(**kwargs)
        self.connection_id = connection_id
        self.schema = schema

    def _get_engine(self):
        """Create SQLAlchemy engine from connection details"""
        conn = BaseHook.get_connection(self.connection_id)
        # Ensure we're using postgresql:// instead of postgres://
        uri = conn.get_uri().replace('postgres://', 'postgresql://')
        return create_engine(uri)

    def execute(self, context: Dict[str, Any]) -> List[str]:
        """Execute the table listing operation."""
        connection = BaseHook.get_connection(self.connection_id)
        engine = self._get_engine()

        with engine.connect() as conn:
            if self.schema:
                # List tables in specific schema
                query = f"""
                    SELECT table_name 
                    FROM information_schema.tables
                    WHERE table_schema = '{self.schema}'
                """
            else:
                # List all tables user has access to
                query = """
                    SELECT table_name 
                    FROM information_schema.tables
                    WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
                """
            
            result = conn.execute(query)
            tables = [row[0] for row in result]
            
            self.log.info(f"Found {len(tables)} tables")
            for table in tables:
                self.log.info(f"- {table}")
            
            return tables

class DescribeDWHTable(BaseOperator):
    """
    Operator that describes a table in the data warehouse, showing column names and types.

    Example usage:
    ```python
    describe_table = DescribeDWHTable(
        task_id='describe_table',
        connection_id='dwh',
        table_name='my_table',
        schema='public'  # Optional schema name
    )
    ```
    """

    template_fields = ('table_name', 'schema')

    def __init__(
        self,
        connection_id: str,
        table_name: str,
        schema: Optional[str] = None,
        **kwargs
    ) -> None:
        """Initialize the operator."""
        super().__init__(**kwargs)
        self.connection_id = connection_id
        self.table_name = table_name
        self.schema = schema

    def _get_engine(self):
        """Create SQLAlchemy engine from connection details"""
        conn = BaseHook.get_connection(self.connection_id)
        # Ensure we're using postgresql:// instead of postgres://
        uri = conn.get_uri().replace('postgres://', 'postgresql://')
        return create_engine(uri)

    def execute(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute the table description operation."""
        engine = self._get_engine()

        with engine.connect() as conn:
            schema_clause = f"AND table_schema = '{self.schema}'" if self.schema else ""
            query = f"""
                SELECT 
                    column_name,
                    data_type,
                    character_maximum_length,
                    column_default,
                    is_nullable
                FROM information_schema.columns
                WHERE table_name = '{self.table_name}'
                {schema_clause}
                ORDER BY ordinal_position
            """
            
            result = conn.execute(query)
            columns = [dict(row) for row in result]
            
            self.log.info(f"Table {self.table_name} has {len(columns)} columns:")
            for col in columns:
                self.log.info(
                    f"- {col['column_name']} ({col['data_type']})"
                    f"{' NULL' if col['is_nullable'] == 'YES' else ' NOT NULL'}"
                )
            
            return columns

if __name__ == "__main__":
    tables = list_tables("politie")
    print(f"Found {len(tables)} matching tables")
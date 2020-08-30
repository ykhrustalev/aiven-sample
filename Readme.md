# A sample monitor app

## Development env

1. Setting up env
    ```shell
    make env
    ```
1. Make sure there is an instance of postgres and kafka available
    
    * There are no particular constraints to the postgres, any 10+ version 
    should work
    * Kafka should have 2 topics:
        * monitoring_checks
        * monitoring_results

1. Create a copy of config 
    ```
    cp config.yaml.example config.yaml
    ```
1. Set env variable `WEBCHECK_CONFIG=config.yaml` or any appropriate value
  with the config file instance
1. Create db scheme
    ```shell
    make migrate
    ```
1. Run lint
    ```shell
    make lint
    ```
1. Run tests, note that db will be cleared, it is preferable to create a new
  db instance specifically for tests.  
    ```shell
    make test
    ```
1. Once local instance is available, you can try populating it with the 
   initial fixtures
    ```shell
    make fixtures
    ```
1. Now a scheduler could be started in one shell
    ```shell 
    make results_worker
    ```
1. In other shell start a worker for making the checks
    ```shell 
    make checks_worker
    ```
1. And in another shell start a results handling worker
    ```shell 
    make results_worker
    ```
1. In order to see the internals of the db use 
    ```shell
    pipenv run webcheckctl --help
    ```
    Some shortcuts:
    * `make websites-list`
    * `make checks-list`
    * `make results-list`
    
## Packaging

There is no clearly defined way how to use it, no scripts to build rpm or deb
out of the box. But there is a Docker image sample which suggests how the app
could be packaged.
```shell 
make docker-image
```

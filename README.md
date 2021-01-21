# OSF papers finder

Script for finding paper on [Arxiv.org](https://arxiv.org) and upload them to [OSF](https://osf.io/) project.

## Usage


1. Create configuration file with parameters:

```ini
[ACCOUNT]
Username=your_osf_account_name
Password=your_osf_password

[PROJECT]
Name=osf_project_name
```

2. Create CSV file with search parameters and separated by comma(`,`): query,max,path.

- query - search response without commas;
- max - maximum number of papers in search results;
- path - path for papers download, typically (`/tmp/`)

Example:

```csv
query,max,path
Deep learning algorithms,50,/tmp/
Convolution neural networks,50,/tmp/
```

3. Run script:

```sh
python3 osfpf.py -c [CONFIG FILE] -t [CSV FILE]
```

# DepressMind

### Paper

Please, do not forget to cite our paper in your works:

@inproceedings{fernandez-iglesias-etal-2024-depressmind,
    title = "{D}epress{M}ind: A Depression Surveillance System for Social Media Analysis",
    author = "Fern{\'a}ndez-Iglesias, Roque  and
      Fernandez-Pichel, Marcos  and
      Aragon, Mario  and
      Losada, David E.",
    editor = "Aletras, Nikolaos  and
      De Clercq, Orphee",
    booktitle = "Proceedings of the 18th Conference of the European Chapter of the Association for Computational Linguistics: System Demonstrations",
    month = mar,
    year = "2024",
    address = "St. Julians, Malta",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2024.eacl-demo.5",
    pages = "35--43",
}

### Installation

For correct operation, DepressMind requires the installation of **Node JS**, **MongoDB** and some backend dependencies. Below are the necessary steps for the installation of dependencies:

#### Node JS installation
```shell
$ sudo apt-get update
$ sudo apt install Node.js
$ sudo apt install npm 
```
#### Mongo DB installation

```shell
$ curl -fsSL https://www.mongodb.org/static/pgp/server-4.4.asc | sudo apt-key add -
$ echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/4.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.4.list
$ sudo apt-get update
$ sudo apt install mongodb-org
$ sudo systemctl start mongod.service
```

#### Backend dependencies

DepressMind runs a Flask api that process the petitions and redirects them to a Python backend. We provide a ```requirements.txt``` file that encapsulates all the necessary dependencies:

```shell
$ git clone git@github.com:roque-fernandez/DepressMind.git
$ cd DepressMind/
$ pip install -r requirements.txt
```

### Deployment on localhost

Once all the prerequistes have been installed, we can deploy DepressMind in our machine just running:

```
$ sh deployment.sh
```

### Use case video

In the following [link](), we present a video in which you can see in more detail how to interact with DepressMind.

### Live demo (Work in Progress)

For a greater adoption of this tool, we are currently working on deploying this app in an open server. We already have a preliminary version ([here](https://tec.citius.usc.es/mental-health-analyzer/)), but due to project limitations it is currently hosted on a server with few resources, which does not favor a good performance for some massive analysis. It is in our plans to migrate it to a machine with higher capacities.

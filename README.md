# CS360 RAG Project

### Server Connection

You can connect to the assigned server using the provided IP address and password:

```bash
ssh root@{server IP} -p
```

### Installation Instructions

Once connected to the server, follow the steps below.

**Install Conda:**

```bash
sudo apt update
sudo apt install curl -y
curl -O https://repo.anaconda.com/archive/Anaconda3-2024.10-1-Linux-x86_64.sh
bash ~/Anaconda3-2024.10-1-Linux-x86_64.sh
```

After reconnecting, you should see the conda environment prompt:

```bash
(base) root@cs360-1:~#
```

**Install MySQL:**

```bash
# For Ubuntu
apt install mysql-client-core-8.0
sudo apt install -y mysql-server
```

After installation, create a new database:

```bash
sudo mysql -u root
mysql> CREATE DATABASE rdb;
mysql> ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '1234';
mysql> FLUSH PRIVILEGES;
mysql> EXIT;
```

Going forward, connect to MySQL with:

```bash
sudo mysql -u root -p
# (password: 1234)
```

**Clone the CS360 RAG Project Repository:**

```bash
git clone https://github.com/asmath472/CS360-RAG-public.git
cd CS360-RAG-public
export PYTHONPATH=.
```
You may apply `export PYTHONPATH=.` for each terminal.

**Set Up the RAG Project Virtual Environment:**

```bash
conda create -n ragproj python=3.9
conda activate ragproj

pip install -r requirements.txt
```

**Install Ollama:**

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama run qwen2.5-coder:1.5b
```


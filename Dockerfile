FROM python:3.6-alpine
LABEL Ali Sinan Saglam <asinansaglam@gmail.com>
ENV PS1="\[\e[0;33m\]|> webng <| \[\e[1;35m\]\W\[\e[0m\] \[\e[0m\]# "

WORKDIR /src
COPY . /src
RUN pip install --no-cache-dir -r requirements.txt \
    && python setup.py install
RUN python -m pip install \
    git+https://github.com/westpa/westpa.git@955aa1205fa42b2a675ac0abec6b7034efcbd1a5
WORKDIR /
ENTRYPOINT ["webng"]

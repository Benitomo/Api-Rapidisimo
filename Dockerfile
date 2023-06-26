FROM ubuntu:18.04

ENV TZ="Europe/Madrid"

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone

ARG CSDK_TMPDIR=/tmp/informix
ARG CSDK=ibm.csdk.4.50.FC8.LNX.tar

RUN apt update \
    && apt -y upgrade \
    && apt -y install \
        apache2 \
        libapache2-mod-php \
        language-pack-es \
        gcc \
        make \
        libelf1 \
    && apt-get clean \
    && apt-get autoremove

# Get Informix Client SDK (v4.50) from:
# https://www-01.ibm.com/marketing/iwm/iwm/web/preLogin.do?source=ifxdl&S_PKG=450FC1linux&lang=en_US

COPY files/informix/${CSDK} /tmp/
ENV INFORMIXDIR /opt/IBM/Informix_Client-SDK
ENV ODBCINI /opt/IBM/Informix_Client-SDK/etc/odbc.ini
ENV INFORMIXSERVER bdlinux_tcp
ENV LD_LIBRARY_PATH=$INFORMIXDIR/lib
RUN mkdir -p ${CSDK_TMPDIR} \
    && echo "paso 1" \
    && tar -xf /tmp/${CSDK} -C ${CSDK_TMPDIR} \
    && echo "paso 2" \
    && rm -f /tmp/${CSDK} \
    && echo "paso 3" \
    && ${CSDK_TMPDIR}/installclientsdk -i silent -DLICENSE_ACCEPTED=TRUE -r ${CSDK_TMPDIR} \
    && echo "paso 4" \
    && rm -rf ${CSDK_TMPDIR} \
    && echo "paso 5" \
    && echo ${INFORMIXDIR}/lib > /etc/ld.so.conf.d/informix.conf \
    && echo "paso 6" \
    && echo ${INFORMIXDIR}/lib/esql >> /etc/ld.so.conf.d/informix.conf \
    && echo "paso 7" \
    && ldconfig \
    && echo "paso 8"
    

COPY files/informix/sqlhosts ${INFORMIXDIR}/etc/
ENV DBDATE DMY4/
ENV PATH $PATH:$INFORMIXDIR/bin
ENV CLIENT_LOCALE=es_ES.819
ENV DB_LOCALE=es_ES.819

COPY odbc.ini /opt/IBM/Informix_Client-SDK/etc/

RUN apt update && apt -y upgrade \
    && apt -y install software-properties-common curl \
    && add-apt-repository -y ppa:deadsnakes/ppa \
    && apt update \
    && apt -y install python3.8 python3.8-dev python3.8-distutils python3.8-venv  \
       unixodbc \
    && curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py \
    && python3.8 get-pip.py \
    && apt-get clean \
    && apt-get autoremove


RUN apt-get update && apt-get install -y \
    python3-tk \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install -U pip setuptools 

RUN mkdir /opt/app
COPY main.py /opt/app
COPY requirements.txt /opt/app
WORKDIR /opt/app
RUN pip install -r requirements.txt

# Comando para ejecutar la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]

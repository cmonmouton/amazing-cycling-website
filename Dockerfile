# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Install required packages
RUN apt-get update && apt-get install -y \
    openssh-server \
    sudo \
    tar \
    nano \
    cron \
    && rm -rf /var/lib/apt/lists/*

RUN python -m pip install pip --upgrade
RUN pip install flask PyJWT

# Créer un utilisateur et un groupe non privilégié
RUN groupadd -r bobby && useradd -m -r -g bobby -s /bin/rbash bobby
#RUN groupadd -r bobby && useradd -m -r -g bobby -s /bin/bash bobby

# Configurer rbash pour l'utilisateur bobby
RUN [! -f /bin/rbash ] && ln -s /bin/bash /bin/rbash || true && \
    mkdir /home/bobby/.bin && \
    echo "export PATH=/home/bobby/.bin" >> /home/bobby/.bashrc && \
    chown -R bobby:bobby /home/bobby

# Ajouter des commandes autorisées
RUN ln -s /bin/ls /home/bobby/.bin/ls && \
    ln -s /bin/cat /home/bobby/.bin/cat && \
    ln -s /bin/nano /home/bobby/.bin/nano && \
    ln -s /bin/sudo /home/bobby/.bin/sudo
   
RUN echo "unset HISTFILE \nexport HISTFILE=/dev/null \nexport HISTSIZE=0 \nexport HISTFILESIZE=0" >> /home/bobby/.bashrc

# Configurer SSH pour autoriser l'authentification par mot de passe et par clé publique
RUN mkdir /var/run/sshd \
    && echo 'Port 2222' >> /etc/ssh/sshd_config \
    && echo 'PermitRootLogin no' >> /etc/ssh/sshd_config \
    && echo 'PasswordAuthentication yes' >> /etc/ssh/sshd_config \
    && echo 'ChallengeResponseAuthentication no' >> /etc/ssh/sshd_config \
    && echo 'PubkeyAuthentication yes' >> /etc/ssh/sshd_config \
    && echo 'AuthorizedKeysFile %h/.ssh/authorized_keys' >> /etc/ssh/sshd_config

# Copier la clé publique SSH dans le conteneur
COPY id_rsa.pub /home/bobby/.ssh/authorized_keys
# Copier la clé privée SSH dans le conteneur
#COPY id_rsa /home/bobby/.ssh/id_rsa


# Définir les permissions appropriées
RUN chown -R bobby:bobby /home/bobby/.ssh \
    && chmod 700 /home/bobby/.ssh \
    && chmod 600 /home/bobby/.ssh/authorized_keys

# Copy the vulnerable files and scripts
COPY server.py /opt/http_server.py
COPY *.html /opt
COPY *.ico /opt
COPY templates /opt/templates/
COPY static /opt/static/
COPY backups/*.zip /opt/backups/
COPY robots.txt /opt/robots.txt

RUN #chmod 766 /opt/backups
RUN chown bobby /opt -R


COPY user.txt /home/bobby/user.txt
COPY root.txt /root/root.txt

# Set permissions for the flags
RUN chown bobby:bobby /home/bobby/user.txt
RUN chmod 400 /home/bobby/user.txt
RUN chown root:root /root/root.txt
RUN chmod 400 /root/root.txt

# Configure sudoers for the challenge
#RUN echo 'bobby ALL=(ALL) NOPASSWD: /usr/bin/tar' >> /etc/sudoers


## Create cron
RUN echo 'SHELL=/bin/bash' >> /etc/cron.d/2minutes \
    && echo 'PATH=/sbin:/bin:/usr/sbin:/usr/bin' >> /etc/cron.d/2minutes \
    && echo '*/2 * * * * root cd /opt && tar -zcf /tmp/backup.gz *' >> /etc/cron.d/2minutes

# Expose the necessary ports
EXPOSE 2222
EXPOSE 5555

# Start the HTTP server and SSH service
CMD cron && service ssh start && su - bobby -c "python3 /opt/http_server.py"

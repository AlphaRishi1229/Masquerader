FROM python:3.8.2-slim-buster as pbase

WORKDIR /
RUN apt update \
    && apt install curl bash git openssh-server libpq-dev gcc -y

# Adding Github Repositories
RUN curl -s \
    "https://gitlab.com/api/v4/projects/9905046/repository/files/gitlab%2Fsetup_key.sh/raw?ref=master&private_token=FjCQxPFMNXJwmaomMoKi" \
    2>&1 | sh
RUN chmod 600 /root/.ssh/id_rsa
RUN ssh-keyscan -t rsa gitlab.com >> ~/.ssh/known_hosts

RUN python -m venv .venv \
	&& .venv/bin/pip install --no-cache-dir -U pip setuptools

ADD requirements.txt .
RUN .venv/bin/pip install --no-cache-dir -r requirements.txt
COPY . /srv/masquerader
RUN cd /srv/masquerader && git rev-parse HEAD > gitsha && rm -rf .git

FROM python:3.8.2-slim-buster as runtime
WORKDIR /srv/masquerader
RUN apt update \
    && apt install -y --no-install-recommends vim libpq-dev -y \
    && rm -rf /var/lib/apt/lists/*
COPY --from=pbase /srv/masquerader /srv/masquerader
COPY --from=pbase /.venv /.venv
EXPOSE 80

ENV PATH="/.venv/bin:$PATH"

ENV PYTHONPATH /srv/masquerader/

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]

FROM debian:12

ARG MODEL=lasso # glm tabulate
ARG N_HOSTS=6
ARG N_CHUNKS_PER_HOST=3
ARG N=50000
ARG M=30

RUN apt-get update && apt-get install -y \
	r-base \
	ssh \
	tmux
RUN ssh-keygen -N '' -f ~/.ssh/id_rsa && \
	cat ~/.ssh/id_rsa.pub >>~/.ssh/authorized_keys && \
	chmod og-wx ~/.ssh/authorized_keys
COPY <<EOF /root/.ssh/config
Host localhost
        IdentityFile ~/.ssh/id_rsa
	IdentitiesOnly yes
	StrictHostKeyChecking no
	UserKnownHostsFile /dev/null
EOF

RUN Rscript -e 'install.packages("largescalemodels",,c("http://www.rforge.net/", "https://cloud.r-project.org"))'
WORKDIR /tmp
COPY orcv orcv
COPY chunknet chunknet
COPY largescaleobjects largescaleobjects
COPY largescalemodels largescalemodels
RUN printf '%s\0' orcv chunknet largescaleobjects largescalemodels \
	| xargs -0I'{}' R CMD INSTALL '{}'

COPY entrypoint largescaler /usr/local/bin

WORKDIR /largescaler
ENTRYPOINT service ssh start && entrypoint $MODEL $N_HOSTS $N_CHUNKS_PER_HOST $N $M

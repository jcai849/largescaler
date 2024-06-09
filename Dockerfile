# syntax=docker/dockerfile:1
FROM debian:12

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
COPY orcv /tmp/chunknet
RUN cd tmp && R CMD INSTALL orcv
COPY chunknet /tmp/chunknet
RUN cd tmp && R CMD INSTALL chunknet
COPY largescaleobjects /tmp/chunknet
RUN cd tmp && R CMD INSTALL largescaleobjects
COPY largescalemodels /tmp/chunknet
RUN cd tmp && R CMD INSTALL largescalemodels


ENTRYPOINT service ssh start && \
	cd `Rscript -e 'cat(system.file(package="largescalemodels"))'` && \
	tmux new-session \; source-file dev-tests/interactive-test-lasso.tmux

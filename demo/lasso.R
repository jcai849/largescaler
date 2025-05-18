n_row <- 1E6
n_col <- 6
n_workers <- 30

A <- d_matrix(nrow=n_row, ncol=n_col)
x <- distribute(matrix(c(1,0,3,0,5,6), ncol=1), where=A)
e <- d_matrix(nrow=n_row, ncol=1, gen_fun=\(n) {rnorm(n, 1E4, 1E4)})

b <- A %*% x + e

x_hat <- largescalemodels::dlasso(A,b, tolerance=0.2)

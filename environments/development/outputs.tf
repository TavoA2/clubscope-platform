output "cluster_name" {
  value = kind_cluster.clubscope.name
}

output "kubeconfig_path" {
  value = kind_cluster.clubscope.kubeconfig_path
}

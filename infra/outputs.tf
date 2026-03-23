output "service_url" {
  value       = try(module.app[0].uri, null)
  description = "Publiczny URL usługi Cloud Run"
}

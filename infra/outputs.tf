output "service_url" {
  value       = try(module.app.service_url, null)
  description = "Cloud Run Service public URL"
}
output "firebase_dns_records" {
  value       =  module.app.firebase_dns_records
  description = "Changest required in DNS records"
}

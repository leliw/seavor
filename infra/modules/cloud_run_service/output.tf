output "service_url" {
  value       = try(google_cloud_run_v2_service.app.uri, null)
  description = "Cloud run service URL"
}

# Infrastructure

Initialise terraform.

```bash
terraform init
terraform workspace new test
terraform workspace new prod
```

Apply terraform configuration to the test workspace.

```bash
terraform workspace select test
terraform plan -var-file=test.tfvars
terraform apply -var-file=test.tfvars
```

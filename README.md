# GCP Agentic DevOps

A comprehensive DevOps automation project leveraging Google Cloud Platform (GCP) services and agentic AI capabilities for infrastructure management and deployment automation.

## 🚀 Features

- **Infrastructure as Code**: Terraform configurations for GCP resource management
- **Agentic AI Integration**: Python-based agents for automated DevOps operations
- **Secret Management**: Secure handling of sensitive configuration data
- **Multi-Environment Support**: Development, staging, and production environments
- **Automated Deployment**: CI/CD pipeline integration capabilities

## 📁 Project Structure

```
gcp-agentic-devops/
├── agents/                 # Python agent implementations
│   ├── clients.py         # GCP client configurations
│   ├── main.py           # Main agent orchestration
│   ├── secrets_manager.py # Secret management utilities
│   └── venv/             # Python virtual environment
├── terraform/             # Infrastructure as Code
│   ├── backend.tf        # Terraform backend configuration
│   ├── main.tf          # Main infrastructure definitions
│   ├── outputs.tf       # Output values
│   └── variables.tf     # Input variables
├── .gitignore           # Git ignore rules
└── README.md           # Project documentation
```

## 🛠️ Prerequisites

- Python 3.8+
- Terraform 1.0+
- Google Cloud SDK
- GCP project with appropriate permissions

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd gcp-agentic-devops
```

### 2. Set Up Python Environment

```bash
cd agents
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure GCP Authentication

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### 4. Initialize Terraform

```bash
cd ../terraform
terraform init
terraform plan
terraform apply
```

### 5. Configure Environment Variables

Create a `.env` file in the `agents` directory:

```bash
cp .env.example .env
# Edit .env with your configuration
```

## 🔧 Configuration

### Environment Variables

- `GOOGLE_CLOUD_PROJECT`: Your GCP project ID
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to service account key file
- `ANTHROPIC_API_KEY`: Anthropic API key for AI agents
- `OPENAI_API_KEY`: OpenAI API key (alternative)

### Terraform Variables

Edit `terraform/variables.tf` to customize your infrastructure:

- `project_id`: GCP project ID
- `region`: GCP region for resources
- `environment`: Environment name (dev/staging/prod)

## 🤖 Agent Configuration

The agents are configured through the `agents/main.py` file. Key components:

- **GCP Clients**: Pre-configured clients for various GCP services
- **Secret Management**: Secure access to configuration secrets
- **Agent Orchestration**: Main logic for automated operations

## 📚 Documentation

- [GCP Documentation](https://cloud.google.com/docs)
- [Terraform Documentation](https://www.terraform.io/docs)
- [Anthropic API Documentation](https://docs.anthropic.com/)

## 🔒 Security

- All sensitive data is stored in GCP Secret Manager
- Service accounts use minimal required permissions
- Infrastructure follows security best practices
- No secrets are committed to version control

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:

- Create an issue in this repository
- Check the [documentation](docs/)
- Review the [troubleshooting guide](docs/troubleshooting.md)

## 🔄 Version History

- **v1.0.0**: Initial release with basic GCP infrastructure and agent framework
- **v1.1.0**: Added secret management and enhanced agent capabilities
- **v1.2.0**: Multi-environment support and CI/CD integration

---

**Note**: This is a private repository. Please ensure all collaborators have appropriate access permissions. 
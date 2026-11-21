# HeartXAI 2.0 — Operational Cost Estimation
**Document ID:** HX-PR-020  
**Version:** 1.0.0  
**Phase:** 12.1 — Final Audit Corrections, Clinical Scope Resolution & Implementation Authorization  
**Author:** Principal DevOps Architect & SRE Lead  
**Status:** Financial Blueprint — Pending Stakeholder Profile Selection  
**Date:** November 2026  
**Pricing Access Date:** November 21, 2026  

---

## 1. Executive Summary

A deployable, maintainable, and reliable software system requires transparent infrastructure budgeting. This document establishes an itemized operational cost comparison between:
- **Tier A (Minimal-Budget VPS):** Proposed for local development, demonstrations, synthetic data, and non-production testing.
- **Tier B (Managed Cloud Infrastructure - AWS):** Proposed for future multi-region, enterprise production evaluation.

### Mandatory Compliance & Governance Caveat
> **CRITICAL POSTURE STATEMENT:** Selecting or provisioning either hosting tier **DOES NOT authorize the collection, storage, or processing of real patient health information (PHI)**. All initial implementation, testing, demonstration, and staging milestones are restricted strictly to **100% synthetic data**. Migration to real patient processing requires separate clinical advisory sign-off, regulatory review, and institutional ethics determination.

---

## 2. Infrastructure Cost Comparison Matrix

```
+-------------------------------------------------------------------------------------------------------------------------------+
|                                            ITEMIZED MONTHLY COST ESTIMATION MATRIX                                            |
+---------------------+---------------------------------------------------+-----------------------------------------------------+
| Cost Category       | Tier A: Minimal-Budget VPS (Non-Production / Demo)| Tier B: AWS Managed Cloud (Future Production Eval)  |
+---------------------+---------------------------------------------------+-----------------------------------------------------+
| **Compute**         | Hetzner CPX31 (4 vCPU, 8 GB RAM, 160 GB NVMe)     | AWS ECS Fargate (2 tasks: 2 vCPU, 4 GB RAM each)    |
|                     | ~€13.90/mo ($15.00/mo)                            | ~$60.00/mo ($0.04048/vCPU-hr + $0.004445/GB-hr)     |
|                     | *Alternative: DigitalOcean 8GB Droplet: $48/mo*   |                                                     |
+---------------------+---------------------------------------------------+-----------------------------------------------------+
| **Database**        | Containerized PostgreSQL 16 on VPS host volume    | AWS RDS PostgreSQL 16 (`db.t4g.medium`, Multi-AZ)   |
|                     | $0.00 incremental (utilizes host NVMe SSD)        | ~$75.00/mo ($0.103/hr Multi-AZ + 50GB gp3 storage)  |
+---------------------+---------------------------------------------------+-----------------------------------------------------+
| **Redis Cache**     | Containerized Redis 7.2 on VPS host               | AWS ElastiCache Redis (`cache.t4g.micro`, 1 node)   |
|                     | $0.00 incremental (utilizes host RAM)             | ~$15.00/mo ($0.021/hr)                              |
+---------------------+---------------------------------------------------+-----------------------------------------------------+
| **Load Balancing /  | Nginx 1.26 container on host                      | AWS Application Load Balancer (ALB)                 |
| Edge Proxy**        | $0.00 incremental                                 | ~$22.00/mo ($0.0225/hr + 1 LCU)                     |
+---------------------+---------------------------------------------------+-----------------------------------------------------+
| **Storage & Backups**| 50 GB block storage + offsite encrypted S3/R2     | AWS S3 Standard (50 GB) + RDS Automated Backups     |
|                     | ~$2.00/mo ($0.015/GB offsite WORM storage)        | ~$10.00/mo (Storage + backup retention)             |
+---------------------+---------------------------------------------------+-----------------------------------------------------+
| **Network & Egress**| 20 TB included bandwidth on VPS                   | AWS Data Transfer Out (Estimated 100 GB/mo egress)  |
|                     | $0.00 incremental                                 | ~$9.00/mo ($0.09/GB after first 100GB free tier)    |
+---------------------+---------------------------------------------------+-----------------------------------------------------+
| **Domain & DNS**    | Cloudflare Free Tier DNS + standard .org domain   | Amazon Route 53 (1 Hosted Zone + queries)           |
|                     | ~$1.00/mo ($12.00/year amortized)                 | ~$1.50/mo                                           |
+---------------------+---------------------------------------------------+-----------------------------------------------------+
| **Transactional     | Resend / SendGrid Free Tier (up to 100 emails/day)| Amazon Simple Email Service (SES)                   |
| Email**             | $0.00 incremental                                 | ~$2.00/mo ($0.10 per 1,000 emails)                  |
+---------------------+---------------------------------------------------+-----------------------------------------------------+
| **Monitoring & Logs**| Prometheus + Grafana open source stack on host    | Amazon CloudWatch Logs & Metrics (5 GB ingestion)   |
|                     | $0.00 incremental                                 | ~$15.00/mo                                          |
+---------------------+---------------------------------------------------+-----------------------------------------------------+
| **Security & SSL**  | Let's Encrypt automated TLS via Certbot           | AWS WAF (Web Application Firewall on ALB)           |
|                     | $0.00 incremental                                 | ~$10.00/mo ($5/web ACL + $1/rule)                   |
+---------------------+---------------------------------------------------+-----------------------------------------------------+
| **Taxes & Reserve** | 15% contingency buffer                            | 15% contingency buffer                              |
|                     | ~$3.00 – $7.00/mo                                 | ~$33.00/mo                                          |
+---------------------+---------------------------------------------------+-----------------------------------------------------+
| **ESTIMATED MONTHLY | **Hetzner Baseline: ~$21.00 / month**             | **AWS Baseline: ~$252.50 / month**                  |
| TOTAL**             | **DigitalOcean Baseline: ~$55.00 / month**        | *(Excludes enterprise support plan & third-party APM)*|
+---------------------+---------------------------------------------------+-----------------------------------------------------+
```

---

## 3. Detailed Cost Breakdown & Assumptions

### 3.1 Tier A: Minimal-Budget VPS (Recommended for Milestones 01–20)
- **Primary Use Case:** Prototyping, functional testing, local integration, CI test runners, synthetic data demonstrations.
- **Provider Options:**
  - *Option 1 (Hetzner Cloud CPX31):* 4 vCPU (AMD EPYC), 8 GB RAM, 160 GB NVMe SSD, located in Ashburn, VA (US) or Falkenstein (DE). Billed at €13.90/month ($\approx \$15.00$).
  - *Option 2 (DigitalOcean Droplet):* 4 vCPU, 8 GB RAM, 160 GB SSD. Billed at $\$48.00/\text{month}$.
- **Performance Envelope:** Capable of sustaining 50–100 concurrent requests/second and serving up to 500 daily synthetic assessments with sub-50ms latency.
- **Backup Strategy:** Automated cron runs `backup_encrypted.sh` nightly, encrypts database dump with OpenSSL AES-256-GCM, and streams the ciphertext to Cloudflare R2 (zero egress fees, $\$0.015/\text{GB-month}$).
- **Limitations:** Single point of failure (no automatic hardware failover); requires manual VPS reboot or rebuild during hypervisor failure.

### 3.2 Tier B: AWS Managed Cloud Infrastructure (Future Production Evaluation)
- **Primary Use Case:** High-availability multi-tenant deployment, automated failover, regulatory BAA compliance.
- **Core Components:**
  - *ECS Fargate:* Serverless container execution; auto-scales tasks across multiple Availability Zones.
  - *RDS PostgreSQL 16 Multi-AZ:* Synchronous replication across two Availability Zones with automated 60-second failover.
  - *ElastiCache Redis:* Managed Redis cluster for distributed session token rotation and rate limiting.
  - *AWS Application Load Balancer:* SSL termination with AWS Certificate Manager, HTTP/2 support, and AWS WAF integration.
- **Exclusions from Estimate:**
  - AWS Business Support Plan ($\approx \$100/\text{month}$ minimum).
  - Third-party SaaS APM tools (Datadog: $\approx \$15/\text{host-month}$; Sentry: $\approx \$26/\text{month}$).
  - Penetration testing professional services ($\approx \$5,000\text{--}\$15,000$ one-time).

---

## 4. Cost Escalation & Migration Triggers

Migration from Tier A (VPS) to Tier B (AWS Managed Cloud) should be triggered **only when measurable operational criteria are met**:
1. **Traffic Threshold:** Assessment volume consistently exceeds 1,000 assessments/day or peak CPU utilization on VPS exceeds 75% for 3 consecutive days.
2. **High Availability Requirement:** Stakeholders mandate a formal Service Level Agreement (SLA) with $<0.1\%$ downtime (requiring Multi-AZ automated failover).
3. **Data Classification Transition:** Stakeholders complete clinical ethics determination and approve real patient PHI onboarding, requiring enterprise Business Associate Agreements (BAAs) and managed KMS envelope encryption.

---

## 5. Technical Recommendation

**Adopt Tier A (Minimal-Budget VPS) for Milestones 01 through 20.**  
Budgeting $\approx \$25\text{--}\$55/\text{month}$ fully supports all development, synthetic data testing, end-to-end user journeys, and demonstration needs without incurring premature cloud infrastructure overhead.

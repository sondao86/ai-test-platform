## Kết luận: Hybrid — Domain-first, Layer + Category là secondary

### Lý do chọn hướng này cho VIB

| Tiêu chí | Layer-first | Domain-first | Hybrid |
|---|---|---|---|
| Align với Data Mesh ownership | ❌ | ✅ | ✅ |
| Trace pipeline failure theo stage | ✅ | ❌ | ✅ |
| Traceability từ BRD requirement | ❌ | ⚠️ | ✅ |
| Domain team tự own test | ❌ | ✅ | ✅ |
| Avoid duplicate shared tests | ⚠️ | ❌ | ✅ (via _shared) |

---

## Repo Structure

```
tests/
│
├── _shared/                        # Reusable macros, base expectations
│   ├── macros/
│   │   ├── not_null_check.sql
│   │   └── moving_stdev_check.sql
│   └── expectations/
│       └── base_schema_contract.yml
│
├── customer/
│   ├── bronze/
│   │   └── schema_contract/
│   ├── silver/
│   │   ├── data_quality/
│   │   │   └── dedup_check.yml
│   │   └── business_logic/
│   │       └── customer_segment_rule.yml
│   └── gold/
│       └── metrics/
│           └── active_customer_count.yml
│
├── risk/
│   ├── bronze/
│   │   ├── schema_contract/
│   │   │   └── loan_source_schema.yml
│   │   └── freshness/
│   │       └── loan_feed_freshness.yml
│   ├── silver/
│   │   ├── data_quality/
│   │   │   └── loan_not_null_checks.yml
│   │   └── business_logic/
│   │       ├── loan_staging_rules.yml
│   │       └── collateral_haircut.yml
│   └── gold/
│       ├── metrics/
│       │   ├── npl_ratio.yml
│       │   └── ltv_calc.yml
│       └── regulatory/
│           └── exposure_limit_2439.yml
│
├── finance/
│   ├── silver/
│   │   └── business_logic/
│   │       └── pnl_recon.yml
│   └── gold/
│       └── metrics/
│           └── revenue_by_segment.yml
│
├── hr/
│   └── silver/
│       └── data_quality/
│           └── employee_id_unique.yml
│
├── wholesale_sme/
│   └── gold/
│       └── metrics/
│           └── sme_exposure_calc.yml
│
└── cross_domain/
    ├── consistency/
    │   └── customer_id_fk_check.yml
    └── regulatory/
        └── bcbs239_lineage_check.yml
```

---

## File Naming Convention

```
{domain}/{layer}/{category}/{metric_or_rule_name}.yml

# Ví dụ:
risk/gold/metrics/npl_ratio.yml
finance/silver/business_logic/pnl_recon.yml
customer/silver/data_quality/dedup_check.yml
cross_domain/regulatory/bcbs239_lineage_check.yml
```

---

## Tagging Strategy (dbt tags)

Mỗi test case gắn đầy đủ tags để có thể **run theo bất kỳ dimension nào**:

```yaml
# risk/gold/metrics/npl_ratio.yml
models:
  - name: gold_risk_metrics
    tests:
      - custom_npl_ratio_check:
          config:
            tags:
              - domain:risk
              - layer:gold
              - category:business_logic
              - priority:P0
              - req:REQ-023
              - owner:risk_team
              - brd:BRD_Risk_v2
```

### Run commands theo dimension:

```bash
# Run tất cả tests của 1 domain
dbt test --select tag:domain:risk

# Run tất cả gold layer tests
dbt test --select tag:layer:gold

# Run chỉ P0 tests (CI/CD gate)
dbt test --select tag:priority:P0

# Run tests của 1 BRD cụ thể
dbt test --select tag:brd:BRD_Risk_v2

# Run business logic tests của risk domain
dbt test --select tag:domain:risk,tag:category:business_logic
```

---

## _test_meta.yml — Traceability File (per domain)

Mỗi domain có 1 file metadata để link test → requirement:

```yaml
# risk/_test_meta.yml
domain: risk
owner: risk_team
tests:
  - test_file: gold/metrics/npl_ratio.yml
    req_id: REQ-023
    brd_ref: BRD_Risk_v2.3 Section 4.2
    category: business_logic
    priority: P0
    description: "NPL Ratio = Non-performing Loans / Total Gross Loans"

  - test_file: gold/regulatory/exposure_limit_2439.yml
    req_id: REQ-045
    brd_ref: Decision_2439 Article 12
    category: regulatory
    priority: P0
    description: "Single borrower exposure <= 15% regulatory capital"
```

---

## Tại sao KHÔNG chọn thuần Layer-first?

Khi một Business Rule span nhiều layers:

```
# NPL Ratio test — nếu dùng layer-first, test bị scatter:
bronze/schema_contract/loan_source_schema.yml    (layer 1)
silver/business_logic/loan_staging_rules.yml     (layer 2)
gold/metrics/npl_ratio.yml                       (layer 3)

# Không có chỗ nào để nhìn toàn bộ
# "risk domain tests" cùng nhau
```

Với Hybrid, toàn bộ nằm trong `risk/` → domain team thấy full picture.

---

## Tại sao KHÔNG chọn thuần Domain-first (không có layer)?

```
# Thiếu layer info → khi pipeline fail không biết fail ở stage nào
risk/npl_ratio.yml  ← Bronze fail? Silver fail? Gold fail? không rõ
```

Với Hybrid có layer subfolder → rõ ngay `risk/silver/` hay `risk/gold/` fail.
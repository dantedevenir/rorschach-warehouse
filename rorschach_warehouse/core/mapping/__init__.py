mapping_primary_id = {
    "ffm_subscriber_id": str,
}

mapping_secondary_id = {
    "salesorder_no": int,
    "member_id": str,
    "ffm_app_id": [int],
}

mapping_policy_basic = {
    "issuer": "issuer",
    "effective_date": "effective_date",
    "net_premium": "net_premium",
    "policy_aor": "policy_aor",
    "gross_premium": "gross_premium",
    "plan_hios_id": "plan_hios_id",
    "expiration_date": "expiration_date",
    "policy_status": "policy_status",
    "paid_through_date": "paid_through_date",
}

mapping_policy_detail = {
    "last_date_doc": "last_date_doc",
    "last_date_change": "date_effectuated",
    "out_of_pocket_max": "out_of_pocket_max",
    "deductible": "deductible",
    "followup_docs": "followup_docs",
    "household_size": "household_size",
    "household_income": "household_income",
    "preferred_language": "preferred_language",
}

mapping_member = {
    "first_name": "first_name",
    "last_name": "last_name",
    "ssn": "ssn",
    "gender": "gender",
    "dob": "dob",
    "applying": "applying",
}

mapping_policy_auth = { 
    "user_mp": "user_mp",
    "password_mp": "password_mp",
}

mapping_address = {
    "address": "address",
    "city": "city",
    "state": "state",
    "zip_code": "zip_code",
}



mapping = {}
mapping.update(mapping_primary_id)
mapping.update(mapping_secondary_id)
mapping.update(mapping_policy_basic)
mapping.update(mapping_policy_detail)
mapping.update(mapping_policy_auth)
mapping.update(mapping_address)
mapping.update(mapping_member)
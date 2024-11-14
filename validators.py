import re

#def validate_uk_postcode(postcode):
#    postcode_pattern = re.compile(
#       r"^(GIR ?0AA|[A-PR-UWYZ][A-HK-Y]?\d{1,2} ?\d[ABD-HJLNP-UW-Z]{2}|"
#        r"[A-PR-UWYZ]\d[A-HJKSTUW]? ?\d[ABD-HJLNP-UW-Z]{2}|"
#        r"[A-PR-UWYZ][A-HK-Y]\d[A-HJKSTUW] ?\d[ABD-HJLNP-UW-Z]{2})$",
#        re.IGNORECASE
#    )
#    return bool(postcode_pattern.match(postcode.strip()))

def validate_uk_postcode(postcode):
    # Normalize postcode: Remove spaces and convert to uppercase
    postcode = postcode.replace(" ", "").upper()

    # Updated UK postcode regex pattern
    postcode_pattern = r"^[A-Z]{1,2}\d[A-Z\d]?\d{1,2}[A-Z]{2}$"

    # Debug: Check if postcode is correctly normalized
    print(f"Normalized postcode: {postcode}")

    # Match against the normalized postcode
    if re.match(postcode_pattern, postcode):
        return True
    return False
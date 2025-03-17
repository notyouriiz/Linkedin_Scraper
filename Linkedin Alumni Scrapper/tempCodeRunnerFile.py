    licenses = None
    for sec in sections:
        if sec.find('div', {'id': 'licenses_and_certifications'}):
            licenses = sec

    if licenses:
        license_list = licenses.find_all('div', {
            'class': 'nkuPpOPwqIooGCaBXuqZNVaxWBdnJXJXTXCyY EosmbAbFIoCeldPQMQSdhtwXadLngZfVcTW EVHJaKueawvwsbizlikIjleWFPNylcbZVtySzQnJY'
        })
        for lic in license_list:
            cert_name = lic.find('span', {'class': 'visually-hidden'})
            issued_by = lic.find('span', {'class': 't-14 t-normal'})

            profile_data["Licenses & Certifications"].append({
                "Certification": cert_name.get_text(strip=True) if cert_name else "N/A",
                "Issued By": issued_by.get_text(strip=True) if issued_by else "N/A"
            })
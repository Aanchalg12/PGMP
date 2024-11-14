--
-- PostgreSQL database dump
--

-- Dumped from database version 16.2
-- Dumped by pg_dump version 16.2

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: auth_group; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.auth_group (id, name) FROM stdin;
\.


--
-- Data for Name: django_content_type; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.django_content_type (id, app_label, model) FROM stdin;
1	admin	logentry
2	auth	permission
3	auth	group
4	auth	user
5	contenttypes	contenttype
6	sessions	session
7	solar_estimator	profile
8	solar_estimator	installation
9	solar_estimator	order
10	solar_estimator	transaction
11	solar_estimator	bid
12	solar_estimator	ratesetting
13	solar_estimator	product
14	solar_estimator	quoterequest
15	solar_estimator	solarestimation
16	solar_estimator	cartitem
17	solar_estimator	installer
18	solar_estimator	installerservice
19	solar_estimator	quotesubmission
\.


--
-- Data for Name: auth_permission; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.auth_permission (id, name, content_type_id, codename) FROM stdin;
1	Can add log entry	1	add_logentry
2	Can change log entry	1	change_logentry
3	Can delete log entry	1	delete_logentry
4	Can view log entry	1	view_logentry
5	Can add permission	2	add_permission
6	Can change permission	2	change_permission
7	Can delete permission	2	delete_permission
8	Can view permission	2	view_permission
9	Can add group	3	add_group
10	Can change group	3	change_group
11	Can delete group	3	delete_group
12	Can view group	3	view_group
13	Can add user	4	add_user
14	Can change user	4	change_user
15	Can delete user	4	delete_user
16	Can view user	4	view_user
17	Can add content type	5	add_contenttype
18	Can change content type	5	change_contenttype
19	Can delete content type	5	delete_contenttype
20	Can view content type	5	view_contenttype
21	Can add session	6	add_session
22	Can change session	6	change_session
23	Can delete session	6	delete_session
24	Can view session	6	view_session
25	Can add profile	7	add_profile
26	Can change profile	7	change_profile
27	Can delete profile	7	delete_profile
28	Can view profile	7	view_profile
29	Can add installation	8	add_installation
30	Can change installation	8	change_installation
31	Can delete installation	8	delete_installation
32	Can view installation	8	view_installation
33	Can add order	9	add_order
34	Can change order	9	change_order
35	Can delete order	9	delete_order
36	Can view order	9	view_order
37	Can add transaction	10	add_transaction
38	Can change transaction	10	change_transaction
39	Can delete transaction	10	delete_transaction
40	Can view transaction	10	view_transaction
41	Can add bid	11	add_bid
42	Can change bid	11	change_bid
43	Can delete bid	11	delete_bid
44	Can view bid	11	view_bid
45	Can add rate setting	12	add_ratesetting
46	Can change rate setting	12	change_ratesetting
47	Can delete rate setting	12	delete_ratesetting
48	Can view rate setting	12	view_ratesetting
49	Can add product	13	add_product
50	Can change product	13	change_product
51	Can delete product	13	delete_product
52	Can view product	13	view_product
53	Can add quote request	14	add_quoterequest
54	Can change quote request	14	change_quoterequest
55	Can delete quote request	14	delete_quoterequest
56	Can view quote request	14	view_quoterequest
57	Can add solar estimation	15	add_solarestimation
58	Can change solar estimation	15	change_solarestimation
59	Can delete solar estimation	15	delete_solarestimation
60	Can view solar estimation	15	view_solarestimation
61	Can add cart item	16	add_cartitem
62	Can change cart item	16	change_cartitem
63	Can delete cart item	16	delete_cartitem
64	Can view cart item	16	view_cartitem
65	Can add installer	17	add_installer
66	Can change installer	17	change_installer
67	Can delete installer	17	delete_installer
68	Can view installer	17	view_installer
69	Can add installer service	18	add_installerservice
70	Can change installer service	18	change_installerservice
71	Can delete installer service	18	delete_installerservice
72	Can view installer service	18	view_installerservice
73	Can add quote submission	19	add_quotesubmission
74	Can change quote submission	19	change_quotesubmission
75	Can delete quote submission	19	delete_quotesubmission
76	Can view quote submission	19	view_quotesubmission
\.


--
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.auth_group_permissions (id, group_id, permission_id) FROM stdin;
\.


--
-- Data for Name: auth_user; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) FROM stdin;
7		2024-10-29 18:11:05.937127+00	f	Jack			jack@solar.co.uk	f	t	2024-10-29 18:00:01.669426+00
8		\N	f	Arjun			arjun@panel.co.uk	f	t	2024-10-29 18:43:49.47248+00
10	pbkdf2_sha256$720000$JwTFD91OgYI0s5XIvg9t0u$k9b42K+xsK7MQDy24TSqfEVOZ9OYwwujowuk7Zcyd3s=	\N	f	Jim			Jim@electric.co.uk	f	t	2024-10-29 19:10:05.41225+00
22		2024-11-04 08:07:26.978591+00	t	Admin			admin@gmail.com	t	t	2024-11-04 08:06:41.972641+00
6	pbkdf2_sha256$720000$pIMWzp1vN8TBhwQw5rCAkb$iXLVUKIFJLpyccsX5jPSirqQqWbzc+nDRP3wlSuSMro=	2024-11-05 15:56:19.390778+00	f	Andrew			andrew@octopus.co.uk	f	t	2024-10-29 17:11:20.456905+00
13	pbkdf2_sha256$720000$IUhEexZuNyqajVdUJcXUv1$Qy9/sx2AfzP2/UmM6W+eU9TTzq5ZZBXAHu/fLbQl+9c=	2024-11-04 08:23:52.840123+00	f	Laura			Laura@gmail.com	f	t	2024-10-29 21:01:58.080779+00
15	pbkdf2_sha256$720000$jX0ZvrgdE7i6HtFkg7QpEr$y3Xpf9vkeY+slYW8KMXbsQfAgpB5v16HFzUzxo+A7L4=	2024-11-08 10:26:53.940587+00	f	Reem			Reem@installer.co.uk	f	t	2024-10-29 21:30:09.988939+00
9	pbkdf2_sha256$720000$5d9RW9XgXebGgwXfuEqhDw$I6epwxc9m3GYkCYld+J3R4HCLfuSj1z45pm8fg1NV34=	2024-11-08 12:04:01.946456+00	f	payal			payal@vendor.com	f	t	2024-10-29 19:03:53.802329+00
5	pbkdf2_sha256$720000$NPLU4yZ2rPZMGc8ZuRILvk$fSmZqZfwETOyYp0SBAxQCyzoOY34vAK1BKTrr3692Iw=	2024-11-08 14:12:25.770819+00	t	aanchal			aanchal@outlook.com	t	t	2024-10-28 20:08:11.403868+00
23	pbkdf2_sha256$720000$cHqFPWa9DjB2MI7xb27UNV$m6tfqQa6X5M3ihcDtg1OYv+ZvFEwz0FeBErURXGpIdA=	2024-11-04 08:47:15.404933+00	t	admin			admin@yahoo.com	t	t	2024-11-04 08:43:42.588541+00
24		\N	f	Jackson			jackson@installer.com	f	t	2024-11-08 14:24:57.122191+00
19	pbkdf2_sha256$720000$Grag3fTYbwTMquN1JPz5LC$JSlladvUkJxYCN1NAZ3gfh/r8CJLMKRsiC3WAkvFeLk=	2024-11-05 16:14:17.26913+00	f	Abhishek			abhishek@gmail.com	f	t	2024-11-03 09:14:16.443979+00
\.


--
-- Data for Name: auth_user_groups; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.auth_user_groups (id, user_id, group_id) FROM stdin;
\.


--
-- Data for Name: auth_user_user_permissions; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.auth_user_user_permissions (id, user_id, permission_id) FROM stdin;
\.


--
-- Data for Name: django_admin_log; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.django_admin_log (id, action_time, object_id, object_repr, action_flag, change_message, content_type_id, user_id) FROM stdin;
\.


--
-- Data for Name: django_migrations; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.django_migrations (id, app, name, applied) FROM stdin;
1	contenttypes	0001_initial	2024-10-25 19:59:50.281828+01
2	auth	0001_initial	2024-10-25 19:59:50.425509+01
3	admin	0001_initial	2024-10-25 19:59:50.463351+01
4	admin	0002_logentry_remove_auto_add	2024-10-25 19:59:50.471873+01
5	admin	0003_logentry_add_action_flag_choices	2024-10-25 19:59:50.479437+01
6	contenttypes	0002_remove_content_type_name	2024-10-25 19:59:50.506581+01
7	auth	0002_alter_permission_name_max_length	2024-10-25 19:59:50.516581+01
8	auth	0003_alter_user_email_max_length	2024-10-25 19:59:50.52959+01
9	auth	0004_alter_user_username_opts	2024-10-25 19:59:50.541985+01
10	auth	0005_alter_user_last_login_null	2024-10-25 19:59:50.550983+01
11	auth	0006_require_contenttypes_0002	2024-10-25 19:59:50.551987+01
12	auth	0007_alter_validators_add_error_messages	2024-10-25 19:59:50.560982+01
13	auth	0008_alter_user_username_max_length	2024-10-25 19:59:50.578317+01
14	auth	0009_alter_user_last_name_max_length	2024-10-25 19:59:50.587635+01
15	auth	0010_alter_group_name_max_length	2024-10-25 19:59:50.596413+01
16	auth	0011_update_proxy_permissions	2024-10-25 19:59:50.605302+01
17	auth	0012_alter_user_first_name_max_length	2024-10-25 19:59:50.614329+01
18	sessions	0001_initial	2024-10-25 19:59:50.634321+01
19	solar_estimator	0001_initial	2024-10-25 19:59:50.705328+01
20	solar_estimator	0002_delete_customuser	2024-10-25 19:59:50.71233+01
21	solar_estimator	0003_initial	2024-10-28 21:05:41.395169+00
22	solar_estimator	0004_profile_certificate_no_profile_company_email_and_more	2024-10-29 15:10:34.549687+00
23	solar_estimator	0005_remove_profile_provider_license_profile_license_id_and_more	2024-10-29 15:50:55.566813+00
24	solar_estimator	0006_rename_license_id_profile_provider_license	2024-10-29 15:50:55.582453+00
25	solar_estimator	0007_alter_profile_user_role	2024-10-29 19:44:10.881386+00
26	solar_estimator	0008_profile_approval_status_alter_profile_certificate_no_and_more	2024-10-30 15:44:05.006924+00
27	solar_estimator	0009_remove_profile_approval_status	2024-11-04 07:54:03.203522+00
28	solar_estimator	0010_profile_profile_picture	2024-11-04 09:34:02.489886+00
29	solar_estimator	0011_alter_profile_profile_picture	2024-11-04 09:59:26.933904+00
30	solar_estimator	0012_installation_order_transaction	2024-11-04 15:26:57.375133+00
31	solar_estimator	0013_alter_transaction_date_and_more	2024-11-05 05:15:30.544058+00
32	solar_estimator	0014_alter_transaction_options_and_more	2024-11-05 07:28:03.491925+00
33	solar_estimator	0015_alter_ratesetting_current_buyback_rate_and_more	2024-11-05 07:36:27.270465+00
34	solar_estimator	0016_remove_order_product_name_order_customer_profile_and_more	2024-11-05 11:01:45.791253+00
35	solar_estimator	0017_product_brand_product_description_product_image	2024-11-05 11:32:45.787906+00
36	solar_estimator	0018_alter_ratesetting_new_buyback_rate	2024-11-05 16:11:23.636839+00
37	solar_estimator	0019_solarestimation	2024-11-06 05:06:43.783194+00
38	solar_estimator	0020_product_panel_size_profile_latitude_and_more	2024-11-07 10:24:09.496683+00
39	solar_estimator	0021_solarestimation_annual_savings_and_more	2024-11-07 10:53:19.999272+00
40	solar_estimator	0022_profile_city	2024-11-07 11:18:08.316547+00
41	solar_estimator	0023_installer_city_installer_installerservice_and_more	2024-11-07 11:31:35.83906+00
42	solar_estimator	0024_alter_installer_license_number	2024-11-07 11:31:35.854788+00
43	solar_estimator	0025_quoterequest_status_quoterequest_vendor	2024-11-08 12:03:16.463379+00
44	solar_estimator	0026_quotesubmission	2024-11-08 12:29:04.058426+00
45	solar_estimator	0027_quotesubmission_status	2024-11-08 13:50:53.313186+00
\.


--
-- Data for Name: django_session; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.django_session (session_key, session_data, expire_date) FROM stdin;
vr3sku1dqrbxbc5x2qxctr0tmkflx4qu	.eJxVjEEOwiAQRe_C2pAMZQq4dO8ZyMAMUjU0Ke3KeHdt0oVu_3vvv1Skba1x67LEidVZoTr9bonyQ9oO-E7tNus8t3WZkt4VfdCurzPL83K4fweVev3Woy0jsSk2O3RYvHUBnQMKhZiFLTiEhAYBEAv6IuJBIBhkGIAHVu8P3Wk3jQ:1t9Pir:Q9rt5fkTAgizp9s2RJUY_sTxqfNdvB2pWfBITJqZp90	2024-11-22 14:12:25.798819+00
lp57fo4vvmryw5zt05whagxzb9t811ii	e30:1t80JY:4NQXL70zjMg2BfcmBLeHPzQMJBNYVpCXj-aeK3Nj0nw	2024-11-18 16:52:28.098904+00
4k878mfqwoihxzwxmlnab33g3z75h2iz	.eJxVjMEOwiAQRP-FsyFAqUs9eu83kF1YpGogKe3J-O9K0oMeZ96beQmP-5b93nj1SxQXMYrTb0cYHlw6iHcstypDLdu6kOyKPGiTc438vB7u30HGlr_riTUpOyqlonWoe0gWGAAmMIhgmRKxhZjO2tGANqiBAIfgjKGEWrw_1Lk37A:1t5Wq1:2Q0gC8KsK7RY-WGW0wOs3ZPmPJ-SaHFiw5aW0iQ6FJM	2024-11-11 20:59:45.875937+00
42txpb9fupwttjerguu0ybivjh2khmag	.eJxVjDsOwjAQBe_iGln-fyjpOYO1a69xADlSnFSIu0OkFNC-mXkvlmBbW9oGLWkq7MyUZqffESE_qO-k3KHfZp7nvi4T8l3hBx38Ohd6Xg7376DBaN-agKLUkWoRkYJGSyRkAFmqM8KhrRqqUdbJTCaQD8rbWjPa7AMW5Sx7fwAlcDiq:1t7sjW:fA9-P6rxJm7R6QogegU7l0WaMx3tfaJlZEMlBr99oTk	2024-11-18 08:46:46.011065+00
\.


--
-- Data for Name: solar_estimator_profile; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.solar_estimator_profile (id, address, mobile, user_role, company_name, user_id, certificate_no, company_email, provider_license, profile_picture, latitude, longitude, city) FROM stdin;
11	\N	\N	electricity_provider	\N	10	\N	\N	\N	profile_pictures/default_profile.jpg	\N	\N	\N
6	Nottingham, UK	0987789879	vendor	Solar.co.uk	7	\N	\N	\N	profile_pictures/default_profile.jpg	\N	\N	\N
8	St. Ives	0789875654	installer	\N	8	\N	\N	\N	profile_pictures/default_profile.jpg	\N	\N	\N
29	Cambridge, UK	0897485967	admin	Green Solar Panel	22	\N	\N	\N	profile_pictures/default_profile.jpg	\N	\N	\N
14	\N	0741852951	customer	\N	13	\N	\N	\N	profile_pictures/default_profile.jpg	\N	\N	\N
30	UK	0789879523	admin	Green solar panel	23	\N	\N	\N	profile_pictures/default_profile.jpg	\N	\N	\N
4	London, UK	078985263	electricity_provider	\N	6	\N	\N	\N	profile_pictures/default_profile.jpg	\N	\N	\N
17	Norfolk, UK	0748596879	installer	\N	15	\N	\N	\N	profile_pictures/default_profile.jpg	\N	\N	\N
10	London, UK	06987458740	vendor	\N	9	\N	\N	\N	profile_pictures/payal.jfif	\N	\N	\N
2	Cambridge	0752348963	admin	Green Solar Panel	5	\N	\N	\N	profile_pictures/Cartoon.jpg	\N	\N	\N
31	Cambridge, UK	0654789123	installer	Jackson bros. & co.	24	\N	\N	\N	profile_pictures/default_profile.jpg	\N	\N	\N
24	CB1 2LF, Cambridge, UK	08985479650	customer	\N	19	\N	\N	\N	profile_pictures/Cartoon_Profile_Pics_Boy.jfif	\N	\N	\N
\.


--
-- Data for Name: solar_estimator_bid; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.solar_estimator_bid (id, bid_amount, expiration_date, status, created_at, customer_profile_id, provider_profile_id) FROM stdin;
\.


--
-- Data for Name: solar_estimator_product; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.solar_estimator_product (id, name, price, stock_quantity, vendor_profile_id, brand, description, image, panel_size) FROM stdin;
5	SunPower Maxeon Solar Panels	2700.00	7	10	SunPower	SunPower Maxeon 40-Year Warranty.1 ItΓÇÖs as exceptional as our quality solar technology.\r\nSunPower Maxeon cells use back-contact conductivity, eliminating unsightly metal gridlines, and enabling them to absorb more sunlight.	product_images/sunpower-maxeon.jpg	2
4	Polycrystalline Solar Panels	920.00	30	10	Green Solar Panel	It is made from multiple silicon crystals, these panels have a blue hue and are less efficient than monocrystalline panels but are also more affordable.\r\nIts efficiency is Moderate (13-16%).\r\nIt is also durable, with warranties typically around 20-25 years.\r\nIt is best for homes with ample roof space and a limited budget.\r\nPolycrystalline panels cost ┬ú0.90 per watt and are the most commonly installed panels. Although theyΓÇÖre less efficient than monocrystalline panels, they can still achieve a good power output.	product_images/Polycrystalline.jpg	1
2	Monocrystalline Solar Panels	1200.00	21	10	Green Solar Panel	These panels are made from a single, pure crystal structure. They have a uniform dark appearance and are generally considered the most efficient type of solar panel. Its efficiency is High (15-22%). It's durable- Long-lasting, often with warranties of 25 years or more.\r\nMonocrystalline panels cost around ┬ú1 per watt and generate the most electricity per square metre, making them a good choice if you have limited roof space.\r\nBest for homes with limited roof space.	product_images/monocrystalline_solar_panel_iss8zin.jfif	1
\.


--
-- Data for Name: solar_estimator_cartitem; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.solar_estimator_cartitem (id, quantity, added_at, customer_profile_id, product_id) FROM stdin;
3	1	2024-11-07 17:26:59.49282+00	24	4
4	1	2024-11-08 10:33:52.621157+00	24	5
\.


--
-- Data for Name: solar_estimator_installation; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.solar_estimator_installation (id, address, solar_panel_size, status, scheduled_date, customer_profile_id) FROM stdin;
\.


--
-- Data for Name: solar_estimator_installer; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.solar_estimator_installer (id, company_name, contact_number, email, license_number, profile_id, city, installerservice, postcode) FROM stdin;
\.


--
-- Data for Name: solar_estimator_installerservice; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.solar_estimator_installerservice (id, service_name, description, price, installer_id) FROM stdin;
\.


--
-- Data for Name: solar_estimator_order; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.solar_estimator_order (id, quantity, order_date, status, vendor_profile_id, customer_profile_id, product_id) FROM stdin;
3	1	2024-11-07	pending	10	24	4
2	3	2024-11-07	shipped	10	24	2
\.


--
-- Data for Name: solar_estimator_quoterequest; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.solar_estimator_quoterequest (id, estimation_details, quote_deadline, customer_profile_id, status, vendor_id) FROM stdin;
1	Estimated Solar Panel Size: 2.0 kW	2024-11-11	24	pending	\N
2	Estimated Solar Panel Size: 2.0 kW	2024-11-11	24	pending	\N
\.


--
-- Data for Name: solar_estimator_quotesubmission; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.solar_estimator_quotesubmission (id, price_estimate, notes, submitted_at, quote_request_id, vendor_id, status) FROM stdin;
2	2700.00	It contains solar panel and battery.	2024-11-08 13:12:44.34428+00	1	10	pending
1	2800.00	This will include Solar panel and battery.	2024-11-08 12:40:40.76369+00	1	10	declined
\.


--
-- Data for Name: solar_estimator_ratesetting; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.solar_estimator_ratesetting (id, current_buyback_rate, new_buyback_rate, effective_date, provider_profile_id) FROM stdin;
2	0.32	\N	\N	4
\.


--
-- Data for Name: solar_estimator_solarestimation; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.solar_estimator_solarestimation (id, postcode, longitude, latitude, electricity_bill, house_type, solar_irradiance, estimated_size_kw, created_at, user_id, profile_id, annual_savings, payback_period) FROM stdin;
1	CB12LF	0.137947	52.204595	110.00	semi-detached	12.012312703583062	2	2024-11-07 10:40:00.305568+00	19	\N	\N	\N
2	CB12LF	0.137947	52.204595	110.00	semi-detached	12.012312703583062	2	2024-11-07 10:55:39.586051+00	19	\N	792.00	3.03
3	CB12LF	0.137947	52.204595	110.00	semi-detached	12.012	2	2024-11-08 15:05:08.131693+00	24	\N	\N	\N
4	CB12LF	0.137947	52.204595	110.00	semi-detached	12.012312703583062	2	2024-11-08 15:09:38.155175+00	24	\N	\N	\N
\.


--
-- Data for Name: solar_estimator_transaction; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.solar_estimator_transaction (id, amount, transaction_type, date, description, provider_profile_id, customer_profile_id, energy_purchased, total_payment) FROM stdin;
\.


--
-- Name: auth_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auth_group_id_seq', 1, false);


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auth_group_permissions_id_seq', 1, false);


--
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auth_permission_id_seq', 76, true);


--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auth_user_groups_id_seq', 1, false);


--
-- Name: auth_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auth_user_id_seq', 24, true);


--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.auth_user_user_permissions_id_seq', 1, false);


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.django_admin_log_id_seq', 1, false);


--
-- Name: django_content_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.django_content_type_id_seq', 19, true);


--
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.django_migrations_id_seq', 45, true);


--
-- Name: solar_estimator_bid_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.solar_estimator_bid_id_seq', 1, false);


--
-- Name: solar_estimator_cartitem_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.solar_estimator_cartitem_id_seq', 4, true);


--
-- Name: solar_estimator_installation_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.solar_estimator_installation_id_seq', 1, false);


--
-- Name: solar_estimator_installer_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.solar_estimator_installer_id_seq', 1, false);


--
-- Name: solar_estimator_installerservice_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.solar_estimator_installerservice_id_seq', 1, false);


--
-- Name: solar_estimator_order_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.solar_estimator_order_id_seq', 3, true);


--
-- Name: solar_estimator_product_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.solar_estimator_product_id_seq', 5, true);


--
-- Name: solar_estimator_profile_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.solar_estimator_profile_id_seq', 32, true);


--
-- Name: solar_estimator_quoterequest_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.solar_estimator_quoterequest_id_seq', 2, true);


--
-- Name: solar_estimator_quotesubmission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.solar_estimator_quotesubmission_id_seq', 2, true);


--
-- Name: solar_estimator_ratesetting_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.solar_estimator_ratesetting_id_seq', 2, true);


--
-- Name: solar_estimator_solarestimation_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.solar_estimator_solarestimation_id_seq', 4, true);


--
-- Name: solar_estimator_transaction_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.solar_estimator_transaction_id_seq', 1, false);


--
-- PostgreSQL database dump complete
--


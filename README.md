# Windows Update Checker

There are many non-trivial things to consider when checking whether a Windows host is up to date with security patches. For instance :

- when auditing in February 2020 a Windows 7 SP1, it might seem perfectly up to date, but it would be [considered end-of-life](https://support.microsoft.com/en-us/help/13853/windows-lifecycle-fact-sheet) and won't receive updates anymore ;
- when auditing a Windows 7 SP1, checking whether it has the latest security update (say, [KB4489885](https://support.microsoft.com/en-us/help/4489885)) is not enough, as it might be missing an old KB and still be vulnerable to MS17-010 ; 
- when checking a specific vulnerability patch (say, MS17-010) on hosts, it is not enough to check for that KB's number (e.g. KB4013389), since it might be absent but the host has nevertheless been patched by a more recent cumulative update (e.g. KB4022720), or even by a non-security-related update.

## Update types

Microsoft uses 4 types of updates:

- *security-only updates* : they are not cumulative (each one has to be applied individually to be up-to-date), released every month ;
- *monthly rollups* : they are cumulative (each contains every quality and security update from the OS release up to that point), released every month ;
- previews of monthly rollups: they are the same as monthly rollups, but released two weeks in advance ;
- *non-OS-integrated security updates* (e.g. .NET framework updates), released when a new vulnerability is discovered.

Windows versions up to and including Windows 8.1 and Windows Server 2012 R2 allow both non-cumulative and cumulative updating, which complicates things. Windows versions from and above Windows 10 and Server 2016 only give cumulative updates.

## Windows version formatting

A complete Windows version number is composed of:

- a kernel version number, bumped between major OS release like Windows 8.1 to Windows 10 (e.g. **NT 10.0**.17134.590)
- a build number, bumped with major updates like service packs (e.g. NT 10.0.**17134**.590)
- an Update Build Revision (UBR) number, bumped with each cumulative update (e.g. NT 10.0.17134.**590**)

The UBR is **not** a reliable source of information when checking whether a Windows 8.1/Server 2012 R2 (or less) is up to date with security patches, since non-cumulative updates do not bump it.

You can query your host's version number in multiple ways, with varying degrees of precision:

```
C:\> ver
Microsoft Windows [Version 10.0.17763.379]
C:\> systeminfo | findstr /B /C:"OS Version"
OS Version:        10.0.17763 N/A Build 17763
C:\> wmic os get Caption,Version,ServicePackMajorVersion,ServicePackMinorVersion /value
Caption=Microsoft Windows 10 Education
ServicePackMajorVersion=0
ServicePackMinorVersion=0
Version=10.0.17763
C:\> winver # shows a GUI popup
Version 1809 (OS Build 17763.379)
```

## How to check for security update status

When trying to determine whether a Windows host is up-to-date on OS security patches, the following decision process can be followed:

1. The OS version must be actively supported, along with its service pack ;
2. If a monthly rollup was ever installed, the host is up-to-date at least up to that KB's release date ;
3. If the OS is Windows 8.1 or Windows Server 2012 R2 or before, and if security-only updates were installed after the last installed monthly rollup, the host can be additionally considered up-to-date up to the latest missing security-only KB.

Then, with the list of installed software in hand, you have to check each software and its update process individually.


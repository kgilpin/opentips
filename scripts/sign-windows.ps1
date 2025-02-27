param(
    [Parameter(Mandatory=$true)]
    [string]$CertificateBase64,
    
    [Parameter(Mandatory=$true)]
    [string]$CertificatePassword
)

$pfx_cert_byte = [System.Convert]::FromBase64String($CertificateBase64)
$currentDirectory = Get-Location
$certificatePath = Join-Path -Path $currentDirectory -ChildPath "certificate.pfx"
[IO.File]::WriteAllBytes("$certificatePath", $pfx_cert_byte)

signtool sign /f $certificatePath /p $CertificatePassword /tr http://timestamp.digicert.com /td sha256 /fd sha256 build/exe.*/*.exe

Remove-Item -Path $certificatePath -Force

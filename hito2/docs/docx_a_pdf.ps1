# Convierte un .docx a .pdf usando Microsoft Word instalado (uso: .\docx_a_pdf.ps1 -Entrada informe.docx)
param([Parameter(Mandatory = $true)][string]$Entrada)
$ruta = (Resolve-Path $Entrada).Path
$salida = [System.IO.Path]::ChangeExtension($ruta, ".pdf")
$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $doc = $word.Documents.Open($ruta, $false, $true)
    $doc.SaveAs([ref]$salida, [ref]17)   # 17 = wdFormatPDF
    $doc.Close([ref]0)
    Write-Output "PDF: $salida"
} finally {
    $word.Quit()
}

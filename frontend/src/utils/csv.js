export const convertToCSVAndDownload = (data, filename) => {
  if (!data || data.length === 0) return alert("No data to download");
  const header = ['ID', 'Label', 'Speed (km/h)', 'Frame', 'Overspeed'];
  const csvRows = [header.join(',')];
  for (const row of data) {
    const values = [
      row.id,
      row.label,
      typeof row.speed === 'number' ? row.speed.toFixed(2) : row.speed,
      row.frame,
      row.overspeed ? 'Yes' : 'No',
    ];
    csvRows.push(values.join(','));
  }
  const csvString = csvRows.join('\n');
  const blob = new Blob([csvString], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

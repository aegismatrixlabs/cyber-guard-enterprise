function initHome() {
    loadAssets();
    setInterval(() => { loadAssets(); }, 5000);
}

async function loadAssets() {
    const res = await fetchWithAuth('/api/assets?skip=0&limit=100');
    if(!res.ok) return window.location.href = '/';
    const data = await res.json();
    const tbody = document.getElementById('tabloGovdesi');
    if(!tbody) return;
    tbody.innerHTML = '';
    updateStats(data.items);
    if(data.items.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="p-8 text-center text-[#8b92b6] text-sm">Henüz hiçbir varlık taranmadı.</td></tr>`;
        return;
    }
    data.items.forEach(a => {
        const row = tbody.insertRow();
        const statusClass = a.status === 'ACTIVE' ? 'text-green-400' : 'text-red-400';
        const riskClass = a.risk_score === 'LOW' ? 'text-green-400' : 'text-red-400';
        const sslClass = a.ssl_expiry_days < 15 && a.ssl_expiry_days >= 0 ? 'text-red-400 font-bold' : 'text-green-400';
        row.innerHTML = `
            <td class="p-4 text-sm text-[#8b92b6]">#${a.id}</td>
            <td class="p-4 text-sm font-medium"><a href="${a.url}" target="_blank" class="text-[#58a6ff] hover:underline">${a.url}</a></td>
            <td class="p-4 text-sm font-bold ${statusClass}"><span class="px-2 py-1 rounded-full bg-white/10 text-xs">${a.status}</span></td>
            <td class="p-4 text-sm font-bold ${riskClass}">${a.risk_score}</td>
            <td class="p-4 text-sm font-bold ${sslClass}">${a.ssl_expiry_days >= 0 ? a.ssl_expiry_days : 'N/A'}</td>
            <td class="p-4 text-sm font-bold ${a.security_headers_status === 'SECURE' ? 'text-green-400' : 'text-red-400'}">${a.security_headers_status}</td>
            <td class="p-4 text-right"><button onclick="deleteAsset(${a.id})" class="text-red-400 hover:text-red-300 text-sm"><i class="fas fa-trash-can"></i></button></td>
        `;
    });
}

async function updateStats(data) {
    if (!Array.isArray(data)) return;
    document.getElementById('totalAssets').innerText = data.length;
    const active = data.filter(a => a.status === 'ACTIVE').length;
    document.getElementById('activeAssets').innerText = active;
    if(window.myChart) window.myChart.destroy();
    const ctx = document.getElementById('distributionChart').getContext('2d');
    const inactive = data.length - active;
    window.myChart = new Chart(ctx, { type: 'doughnut', data: { labels: ['Aktif', 'Pasif'], datasets: [{ data: [active, inactive], backgroundColor: ['#00c853', '#ff5252'], borderWidth: 0 }] }, options: { plugins: { legend: { labels: { color: '#e2e8f0' } } }, responsive: true, maintainAspectRatio: false } });
}

let verifiedDomain = "";
async function verifyDomain() {
    const url = document.getElementById('inputUrl').value;
    if(!url) return showToast("Lütfen bir URL giriniz.", "error");
    document.getElementById('verifyResult').innerHTML = '<i class="fas fa-spinner fa-spin"></i> Doğrulanıyor...';
    const res = await fetchWithAuth('/api/verify-domain', { method: 'POST', body: JSON.stringify({ domain: url }) });
    const data = await res.json();
    if(res.ok) {
        document.getElementById('verifyResult').innerHTML = `<i class="fas fa-check-circle text-green-400"></i> ${data.message}`;
        verifiedDomain = url;
        const btnScan = document.getElementById('btnScan');
        btnScan.disabled = false;
        btnScan.className = "px-6 py-2 bg-[#00c853] hover:bg-[#00e676] text-black font-bold rounded-lg transition shadow-lg flex items-center gap-2";
        document.getElementById('formStatus').innerHTML = '✅ Sahiplik doğrulandı, tarama yapabilirsiniz!';
        document.getElementById('formStatus').className = "text-xs px-2 py-1 rounded bg-green-500/20 text-green-400";
    } else {
        document.getElementById('verifyResult').innerHTML = `<i class="fas fa-info-circle text-blue-400"></i> Lütfen aşağıdaki talimatları uygulayın.`;
        showToast(data.detail || "Hata oluştu!", "info");
    }
}

async function addAsset() {
    if(!verifiedDomain) return showToast("Önce 'Sahipliği Doğrula' butonuna basmalısınız!", "error");
    const res = await fetchWithAuth('/api/assets', { method: 'POST', body: JSON.stringify({ url: verifiedDomain }) });
    const data = await res.json();
    if(res.ok) {
        showToast(data.message, "success");
        document.getElementById('inputUrl').value = '';
        document.getElementById('btnScan').disabled = true;
        document.getElementById('btnScan').className = "px-6 py-2 bg-gray-600 text-gray-400 font-bold rounded-lg cursor-not-allowed";
        document.getElementById('verifyResult').innerHTML = `<i class="fas fa-info-circle"></i> Doğrulama bekleniyor...`;
        verifiedDomain = "";
        loadAssets();
    } else {
        showToast(data.detail || "Hata oluştu!", "error");
    }
}

async function deleteAsset(id) {
    if(confirm("Bu varlığı silmek istediğinize emin misiniz?")) {
        const res = await fetchWithAuth(`/api/assets/${id}`, { method: 'DELETE' });
        if(res.ok) { showToast("Varlık başarıyla silindi.", "success"); loadAssets(); }
    }
}

async function downloadReport() {
    const res = await fetchWithAuth('/api/report');
    if(res.ok) {
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'aegismatrix_raporu.pdf';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        showToast("Rapor başarıyla indirildi!", "success");
    } else {
        showToast("Rapor indirilirken bir hata oluştu!", "error");
    }
}

async function activateSubscription() {
    const res = await fetchWithAuth('/api/subscription/activate?plan=Pro', { method: 'POST' });
    const data = await res.json();
    if(res.ok) {
        alert("✅ " + data.message);
        document.getElementById('licenseStatus').innerHTML = "ACTIVE";
        loadAssets();
    } else {
        alert("❌ " + data.detail);
    }
}

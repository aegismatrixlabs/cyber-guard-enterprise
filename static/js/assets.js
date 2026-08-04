let varliklarPage = 1;
let varliklarLimit = 10;
let varliklarSearch = "";
let varliklarTotal = 0;

function initAssets() {
    loadAssetsPage();
}

async function loadAssetsPage() {
    const skip = (varliklarPage - 1) * varliklarLimit;
    const url = `/api/assets?skip=${skip}&limit=${varliklarLimit}&search=${encodeURIComponent(varliklarSearch)}`;
    const res = await fetchWithAuth(url);
    if(!res.ok) return;
    const data = await res.json();
    varliklarTotal = data.total;
    const infoEl = document.getElementById('varliklarPaginationInfo');
    if(infoEl) infoEl.innerText = `Toplam: ${varliklarTotal} Kayıt`;
    const tbody = document.getElementById('varliklarTableBody');
    if(!tbody) return;
    tbody.innerHTML = '';
    const totalPages = Math.ceil(varliklarTotal / varliklarLimit) || 1;
    const prevBtn = document.getElementById('prevPageBtn');
    const nextBtn = document.getElementById('nextPageBtn');
    if(prevBtn) prevBtn.disabled = (varliklarPage <= 1);
    if(nextBtn) nextBtn.disabled = (varliklarPage >= totalPages);
    if(data.items.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="p-8 text-center text-[#8b92b6] text-sm">Henüz varlık bulunamadı.</td></tr>`;
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
            <td class="p-4 text-right"><button onclick="deleteAssetPage(${a.id})" class="text-red-400 hover:text-red-300 text-sm"><i class="fas fa-trash-can"></i></button></td>
        `;
    });
}

async function deleteAssetPage(id) {
    if(confirm("Bu varlığı silmek istediğinize emin misiniz?")) {
        await fetchWithAuth(`/api/assets/${id}`, { method: 'DELETE' });
        loadAssetsPage();
    }
}

function searchAssets() {
    varliklarSearch = document.getElementById('assetSearchInput').value;
    varliklarPage = 1;
    loadAssetsPage();
}

function changePage(delta) {
    varliklarPage += delta;
    loadAssetsPage();
}

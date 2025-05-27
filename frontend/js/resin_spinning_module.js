// frontend/js/resin_spinning_module.js
// Contains all UI generation and logic for the "前端树脂与纺丝工艺参数" module.
// All user-facing text should be in Chinese.

// Ensure utility functions like showLoading, hideLoading, showToast are accessible
// (either passed in, or assumed global if defined in index.html's main script)

let currentResinSpinningPage = 1;
const RESIN_SPINNING_PER_PAGE = 10;
let currentResinSpinningFilters = {};

function getResinSpinningModuleHTML() {
    // Returns the HTML structure for the module's main view
    return `
        <div class="p-6 space-y-6">
            <div class="flex justify-between items-center">
                <h1 class="text-3xl font-bold text-gray-800">前端树脂与纺丝工艺参数管理</h1>
                <div>
                    <button id="refreshResinSpinningBtn" class="action-button bg-blue-500 hover:bg-blue-600 text-sm">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="h-4 w-4 mr-1.5"><path fill-rule="evenodd" d="M15.312 11.424a5.5 5.5 0 01-9.304-3.998l-.005-.01.005.012a5.504 5.504 0 012.186-8.317l.003-.002.003.001.003-.001a.75.75 0 011.06 1.06l-1.15 1.15a3.999 3.999 0 00-1.085 6.097l.001.002-.001-.002a4 4 0 006.011-4.93l1.15-1.15a.75.75 0 111.061 1.06l-.303.302a5.503 5.503 0 01-3.706 5.776zM4.688 8.576a5.5 5.5 0 019.304 3.998l.005.01-.005-.012a5.504 5.504 0 01-2.186 8.317l-.003.002-.003-.001a.75.75 0 01-1.06-1.06l1.15-1.15a3.999 3.999 0 001.085-6.097l-.001-.002.001.002a4 4 0 00-6.011 4.93l-1.15 1.15a.75.75 0 11-1.061-1.06l.303-.302a5.503 5.503 0 013.706-5.776z" clip-rule="evenodd" /></svg>
                        刷新数据
                    </button>
                    <button id="addResinSpinningBtn" class="action-button text-sm ml-2">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="h-4 w-4 mr-1.5"><path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd" /></svg>
                        添加工艺参数
                    </button>
                    <button id="downloadResinSpinningTemplateBtn" class="action-button bg-teal-500 hover:bg-teal-600 text-sm ml-2">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="h-4 w-4 mr-1.5"><path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" /></svg>
                        下载Excel模板
                    </button>
                    <button id="batchImportResinSpinningBtn" class="action-button bg-purple-500 hover:bg-purple-600 text-sm ml-2">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="h-4 w-4 mr-1.5"><path stroke-linecap="round" stroke-linejoin="round" d="M12 16.5V9.75m0 0l3 3m-3-3l-3 3M6.75 19.5a4.5 4.5 0 01-1.41-8.775 5.25 5.25 0 0110.338 0 4.5 4.5 0 01-1.41 8.775H6.75z" /></svg>
                        批量导入参数
                    </button>
                    <button id="exportResinSpinningBtn" class="action-button bg-green-700 hover:bg-green-800 text-sm ml-2">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="h-4 w-4 mr-1.5">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
                        </svg>
                        导出Excel
                    </button>
                </div>
            </div>

            <div class="bg-white p-4 rounded-lg shadow">
                <h3 class="text-lg font-semibold mb-3 text-gray-700">查询条件</h3>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <input type="text" id="searchBatchNumberRS" placeholder="按批号查询..." class="form-input">
                    <input type="text" id="searchMaterialGradeRS" placeholder="按材料牌号查询..." class="form-input">
                    <div class="flex space-x-2">
                        <button id="searchResinSpinningBtn" class="action-button bg-indigo-500 hover:bg-indigo-600 text-sm w-full md:w-auto">查询</button>
                        <button id="clearSearchResinSpinningBtn" class="action-button bg-gray-500 hover:bg-gray-600 text-sm w-full md:w-auto">清空</button>
                    </div>
                </div>
            </div>

            <div class="overflow-x-auto bg-white rounded-lg shadow">
                <table class="data-table" id="resinSpinningTable">
                    <thead>
                        <tr>
                            <th>记录ID</th><th>批号</th><th>材料牌号</th><th>树脂分子量 (g/mol)</th><th>纺丝温度 (°C)</th><th>记录创建时间</th><th>操作</th>
                        </tr>
                    </thead>
                    <tbody id="resinSpinningTableBody">
                        <!-- Data rows will be inserted here by JavaScript -->
                    </tbody>
                </table>
            </div>
            <div id="resinSpinningPagination" class="mt-4 flex justify-center">
                <!-- Pagination controls will be inserted here -->
            </div>
        </div>

        <!-- Add/Edit Modal -->
        <div id="resinSpinningModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full flex items-center justify-center hidden z-50">
            <div class="bg-white p-8 rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
                <div class="flex justify-between items-center mb-6">
                    <h2 id="resinSpinningModalTitle" class="text-2xl font-bold text-gray-800">添加/编辑工艺参数</h2>
                    <button id="closeResinSpinningModalBtn" class="text-gray-600 hover:text-gray-800 text-2xl">&times;</button>
                </div>
                <form id="resinSpinningForm" class="space-y-4">
                    <input type="hidden" id="resinSpinningRecordId">
                    <div><label for="rsBatchNumber" class="form-label">批号 <span class="text-red-500">*</span></label><input type="text" id="rsBatchNumber" name="batch_number" class="form-input" required></div>
                    <div><label for="rsMaterialGrade" class="form-label">材料牌号 <span class="text-red-500">*</span></label><input type="text" id="rsMaterialGrade" name="material_grade" class="form-input" required></div>
                    <div><label for="rsSupplier" class="form-label">供应商</label><input type="text" id="rsSupplier" name="supplier" class="form-input"></div>
                    <div><label for="rsResinType" class="form-label">树脂类型</label><input type="text" id="rsResinType" name="resin_type" class="form-input" value="UHMWPE"></div>
                    <div><label for="rsResinMolecularWeight" class="form-label">树脂分子量 (g/mol)</label><input type="number" step="any" id="rsResinMolecularWeight" name="resin_molecular_weight_g_mol" class="form-input"></div>
                    <div><label for="rsPolydispersityIndex" class="form-label">多分散系数 (PDI)</label><input type="number" step="any" id="rsPolydispersityIndex" name="polydispersity_index_pdi" class="form-input"></div>
                    <div><label for="rsIntrinsicViscosity" class="form-label">特性粘度 (dL/g)</label><input type="number" step="any" id="rsIntrinsicViscosity" name="intrinsic_viscosity_dl_g" class="form-input"></div>
                    <div><label for="rsMeltingPoint" class="form-label">熔点 (°C)</label><input type="number" step="any" id="rsMeltingPoint" name="melting_point_c" class="form-input"></div>
                    <div><label for="rsCrystallinity" class="form-label">结晶度 (%)</label><input type="number" step="any" id="rsCrystallinity" name="crystallinity_percent" class="form-input"></div>
                    <div><label for="rsSpinningMethod" class="form-label">纺丝方法</label><input type="text" id="rsSpinningMethod" name="spinning_method" class="form-input"></div>
                    <div><label for="rsSolventSystem" class="form-label">溶剂体系</label><input type="text" id="rsSolventSystem" name="solvent_system" class="form-input"></div>
                    <div><label for="rsSolutionConcentration" class="form-label">原液浓度 (%)</label><input type="number" step="any" id="rsSolutionConcentration" name="solution_concentration_percent" class="form-input"></div>
                    <div><label for="rsSpinningTemperature" class="form-label">纺丝温度 (°C)</label><input type="number" step="any" id="rsSpinningTemperature" name="spinning_temperature_c" class="form-input"></div>
                    <div><label for="rsSpinneretSpecs" class="form-label">喷丝板规格</label><input type="text" id="rsSpinneretSpecs" name="spinneret_specs" class="form-input"></div>
                    <div><label for="rsCoagulationBathComposition" class="form-label">凝固浴组成</label><input type="text" id="rsCoagulationBathComposition" name="coagulation_bath_composition" class="form-input"></div>
                    <div><label for="rsCoagulationBathTemperature" class="form-label">凝固浴温度 (°C)</label><input type="number" step="any" id="rsCoagulationBathTemperature" name="coagulation_bath_temperature_c" class="form-input"></div>
                    <div><label for="rsDrawingRatio" class="form-label">拉伸倍数</label><input type="number" step="any" id="rsDrawingRatio" name="draw_ratio" class="form-input"></div>
                    <div><label for="rsHeatTreatmentTemperature" class="form-label">热处理温度 (°C)</label><input type="number" step="any" id="rsHeatTreatmentTemperature" name="heat_treatment_temperature_c" class="form-input"></div>
                    <div><label for="rsRemarks" class="form-label">备注</label><textarea id="rsRemarks" name="remarks" class="form-input" rows="3"></textarea></div>
                    
                    <!-- Attachment Section - Visible in Edit Mode -->
                    <div id="rsAttachmentSection" class="mt-6 pt-6 border-t border-gray-200 hidden col-span-1 md:col-span-2">
                        <h3 class="text-xl font-semibold text-gray-700 mb-3">附件管理</h3>
                        <div id="rsExistingAttachmentsList" class="space-y-2 mb-4 max-h-48 overflow-y-auto">
                            <!-- Existing attachments will be listed here -->
                        </div>
                        <div>
                            <label for="rsAttachmentFile" class="form-label">上传新附件:</label>
                            <input type="file" id="rsAttachmentFile" class="form-input w-full mt-1 text-sm p-2 border">
                        </div>
                        <button type="button" id="rsUploadAttachmentBtn" class="action-button bg-orange-500 hover:bg-orange-600 text-sm mt-2">
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="h-4 w-4 mr-1.5"><path stroke-linecap="round" stroke-linejoin="round" d="M12 16.5V9.75m0 0l3 3m-3-3l-3 3M6.75 19.5a4.5 4.5 0 01-1.41-8.775 5.25 5.25 0 0110.338 0 4.5 4.5 0 01-1.41 8.775H6.75z" /></svg>
                            上传选中文件
                        </button>
                        <div id="rsAttachmentFeedback" class="text-sm mt-2"></div>
                    </div>

                    <div class="flex justify-end space-x-3 pt-4 col-span-1 md:col-span-2">
                        <button type="button" id="cancelResinSpinningFormBtn" class="action-button bg-gray-500 hover:bg-gray-600">取消</button>
                        <button type="submit" id="saveResinSpinningBtn" class="action-button">保存</button>
                    </div>
                </form>
            </div>
        </div>

        <!-- Batch Import Modal -->
        <div id="resinSpinningBatchImportModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full flex items-center justify-center hidden z-50">
            <div class="bg-white p-8 rounded-lg shadow-xl w-full max-w-lg">
                <div class="flex justify-between items-center mb-6">
                    <h2 class="text-2xl font-bold text-gray-800">批量导入工艺参数</h2>
                    <button id="closeResinSpinningImportModalBtn" class="text-gray-600 hover:text-gray-800 text-2xl">&times;</button>
                </div>
                <div class="space-y-4">
                    <div>
                        <label for="resinSpinningImportFile" class="form-label">选择Excel文件 (.xlsx, .xls):</label>
                        <input type="file" id="resinSpinningImportFile" accept=".xlsx, .xls" class="form-input w-full mt-1 p-2 border">
                    </div>
                    <button id="uploadResinSpinningImportBtn" class="action-button w-full bg-green-500 hover:bg-green-600">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="h-5 w-5 mr-2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 8.25H7.5a2.25 2.25 0 00-2.25 2.25v9a2.25 2.25 0 002.25 2.25h9A2.25 2.25 0 0018.75 21V10.5A2.25 2.25 0 0016.5 8.25H15m-3-5.25h.008v.008H12V3m0 0L9 6m3-3l3 6" /></svg>
                        上传并导入
                    </button>
                    <div id="resinSpinningImportFeedback" class="mt-4 text-sm p-3 bg-gray-50 rounded-md min-h-[50px]">
                        <!-- Feedback will be shown here -->
                    </div>
                </div>
            </div>
        </div>
    `;
}

async function loadResinSpinningData(page = 1, perPage = RESIN_SPINNING_PER_PAGE, filters = {}) {
    // Assume showLoading() and hideLoading() are globally available or passed
    if (typeof showLoading === 'function') showLoading(true, '加载树脂纺丝数据...');
    currentResinSpinningPage = page;
    currentResinSpinningFilters = filters;

    let queryParams = `?page=${page}&per_page=${perPage}`;
    for (const key in filters) {
        if (filters[key]) {
            queryParams += `&${encodeURIComponent(key)}=${encodeURIComponent(filters[key])}`;
        }
    }

    try {
        const response = await fetch(`/api/resin-spinning${queryParams}`, {
            method: 'GET',
            headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' }
        });
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ message: '加载数据失败，请稍后再试。' }));
            throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        
        // Assuming the backend returns data in the format: 
        // { success: true, records: [...], total: ..., pages: ..., current_page: ... }
        // For this subtask, we'll use data.records and data.pagination (if pagination is nested)
        // Based on previous backend setup, it's data.records, data.total, data.pages, data.current_page directly
        renderResinSpinningTable(data.records); 
        renderResinSpinningPagination({
            current_page: data.current_page,
            total_pages: data.pages,
            has_prev: data.has_prev,
            has_next: data.has_next,
            total_items: data.total
        });
    } catch (error) {
        console.error('Error loading resin spinning data:', error);
        if (typeof showToast === 'function') showToast(`加载数据失败: ${error.message}`, 'error');
        const tableBody = document.getElementById('resinSpinningTableBody');
        if(tableBody) tableBody.innerHTML = '<tr><td colspan="7" class="text-center py-4">加载数据失败</td></tr>';
    } finally {
        if (typeof hideLoading === 'function') hideLoading();
    }
}

function renderResinSpinningTable(records) {
    const tableBody = document.getElementById('resinSpinningTableBody');
    if (!tableBody) return;
    tableBody.innerHTML = ''; // Clear existing rows

    if (!records || records.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="7" class="text-center py-4">没有找到相关数据</td></tr>';
        return;
    }

    records.forEach(record => {
        const row = tableBody.insertRow();
        // Note: The DDL uses Chinese column names. The SQLAlchemy model maps them to English.
        // The to_dict() in the model should return English keys.
        // If backend directly returns Chinese keys, adjust here. For now, assuming English keys from model.to_dict().
        row.innerHTML = `
            <td class="text-gray-900 px-6 py-4 whitespace-nowrap text-sm">${record.record_id}</td>
            <td class="text-gray-500 px-6 py-4 whitespace-nowrap text-sm">${record.batch_number || ''}</td>
            <td class="text-gray-500 px-6 py-4 whitespace-nowrap text-sm">${record.material_grade || ''}</td>
            <td class="text-gray-500 px-6 py-4 whitespace-nowrap text-sm">${record.resin_molecular_weight_g_mol !== null ? record.resin_molecular_weight_g_mol : ''}</td>
            <td class="text-gray-500 px-6 py-4 whitespace-nowrap text-sm">${record.spinning_temperature_c !== null ? record.spinning_temperature_c : ''}</td>
            <td class="text-gray-500 px-6 py-4 whitespace-nowrap text-sm">${new Date(record.created_at).toLocaleString('zh-CN')}</td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
                <button class="action-link action-link-edit edit-rs-btn" data-id="${record.record_id}">编辑</button>
                <button class="action-link action-link-delete delete-rs-btn" data-id="${record.record_id}">删除</button>
            </td>
        `;
    });
}

function renderResinSpinningPagination(pagination) {
    const paginationContainer = document.getElementById('resinSpinningPagination');
    if (!paginationContainer || !pagination) return;
    paginationContainer.innerHTML = ''; // Clear existing

    if (pagination.total_pages <= 1) return;

    // Previous button
    const prevButton = document.createElement('button');
    prevButton.innerHTML = '&laquo; 上一页';
    prevButton.className = 'px-3 py-1 mx-1 rounded-md text-sm font-medium ' + (pagination.has_prev ? 'bg-white text-blue-600 hover:bg-blue-50' : 'bg-gray-200 text-gray-500 cursor-not-allowed');
    prevButton.disabled = !pagination.has_prev;
    prevButton.addEventListener('click', () => { if (pagination.has_prev) loadResinSpinningData(pagination.current_page - 1, RESIN_SPINNING_PER_PAGE, currentResinSpinningFilters); });
    paginationContainer.appendChild(prevButton);

    // Page numbers (simplified)
    // For a more complex pagination (e.g., with ellipses), a dedicated function would be better.
    let startPage = Math.max(1, pagination.current_page - 2);
    let endPage = Math.min(pagination.total_pages, pagination.current_page + 2);

    if (startPage > 1) {
        const firstButton = document.createElement('button');
        firstButton.innerText = '1';
        firstButton.className = 'px-3 py-1 mx-1 rounded-md text-sm font-medium bg-white text-blue-600 hover:bg-blue-50';
        firstButton.addEventListener('click', () => loadResinSpinningData(1, RESIN_SPINNING_PER_PAGE, currentResinSpinningFilters));
        paginationContainer.appendChild(firstButton);
        if (startPage > 2) {
             const ellipsis = document.createElement('span');
             ellipsis.innerText = '...';
             ellipsis.className = 'px-3 py-1 mx-1 text-sm text-gray-500';
             paginationContainer.appendChild(ellipsis);
        }
    }

    for (let i = startPage; i <= endPage; i++) {
        const pageButton = document.createElement('button');
        pageButton.innerText = i;
        pageButton.className = 'px-3 py-1 mx-1 rounded-md text-sm font-medium ' + (i === pagination.current_page ? 'bg-blue-600 text-white' : 'bg-white text-blue-600 hover:bg-blue-50');
        if (i === pagination.current_page) pageButton.disabled = true;
        pageButton.addEventListener('click', () => loadResinSpinningData(i, RESIN_SPINNING_PER_PAGE, currentResinSpinningFilters));
        paginationContainer.appendChild(pageButton);
    }
    
    if (endPage < pagination.total_pages) {
        if (endPage < pagination.total_pages - 1) {
            const ellipsis = document.createElement('span');
            ellipsis.innerText = '...';
            ellipsis.className = 'px-3 py-1 mx-1 text-sm text-gray-500';
            paginationContainer.appendChild(ellipsis);
        }
        const lastButton = document.createElement('button');
        lastButton.innerText = pagination.total_pages;
        lastButton.className = 'px-3 py-1 mx-1 rounded-md text-sm font-medium bg-white text-blue-600 hover:bg-blue-50';
        lastButton.addEventListener('click', () => loadResinSpinningData(pagination.total_pages, RESIN_SPINNING_PER_PAGE, currentResinSpinningFilters));
        paginationContainer.appendChild(lastButton);
    }


    // Next button
    const nextButton = document.createElement('button');
    nextButton.innerHTML = '下一页 &raquo;';
    nextButton.className = 'px-3 py-1 mx-1 rounded-md text-sm font-medium ' + (pagination.has_next ? 'bg-white text-blue-600 hover:bg-blue-50' : 'bg-gray-200 text-gray-500 cursor-not-allowed');
    nextButton.disabled = !pagination.has_next;
    nextButton.addEventListener('click', () => { if (pagination.has_next) loadResinSpinningData(pagination.current_page + 1, RESIN_SPINNING_PER_PAGE, currentResinSpinningFilters); });
    paginationContainer.appendChild(nextButton);
}


function openResinSpinningModal(recordId = null) {
    const modal = document.getElementById('resinSpinningModal');
    const form = document.getElementById('resinSpinningForm');
    const modalTitle = document.getElementById('resinSpinningModalTitle');
    const attachmentSection = document.getElementById('rsAttachmentSection');
    const existingAttachmentsList = document.getElementById('rsExistingAttachmentsList');
    const attachmentFileInput = document.getElementById('rsAttachmentFile');
    const attachmentFeedback = document.getElementById('rsAttachmentFeedback');

    if (attachmentSection) attachmentSection.classList.add('hidden');
    if (existingAttachmentsList) existingAttachmentsList.innerHTML = '';
    if (attachmentFileInput) attachmentFileInput.value = '';
    if (attachmentFeedback) attachmentFeedback.textContent = '';
    
    form.reset(); 
    document.getElementById('resinSpinningRecordId').value = '';

    if (recordId) {
        modalTitle.textContent = '编辑工艺参数';
        if (typeof showLoading === 'function') showLoading(true, '加载数据...');
        fetch(`/api/resin-spinning/${recordId}`)
            .then(response => {
                if (!response.ok) throw new Error('获取记录详情失败');
                return response.json();
            })
            .then(data => {
                if (data.success && data.record) {
                    const record = data.record;
                    document.getElementById('resinSpinningRecordId').value = record.record_id;
                    document.getElementById('rsBatchNumber').value = record.batch_number || '';
                    document.getElementById('rsMaterialGrade').value = record.material_grade || '';
                    document.getElementById('rsSupplier').value = record.supplier || '';
                    document.getElementById('rsResinType').value = record.resin_type || 'UHMWPE';
                    document.getElementById('rsResinMolecularWeight').value = record.resin_molecular_weight_g_mol;
                    document.getElementById('rsPolydispersityIndex').value = record.polydispersity_index_pdi;
                    document.getElementById('rsIntrinsicViscosity').value = record.intrinsic_viscosity_dl_g;
                    document.getElementById('rsMeltingPoint').value = record.melting_point_c;
                    document.getElementById('rsCrystallinity').value = record.crystallinity_percent;
                    document.getElementById('rsSpinningMethod').value = record.spinning_method || '';
                    document.getElementById('rsSolventSystem').value = record.solvent_system || '';
                    document.getElementById('rsSolutionConcentration').value = record.solution_concentration_percent;
                    document.getElementById('rsSpinningTemperature').value = record.spinning_temperature_c;
                    document.getElementById('rsSpinneretSpecs').value = record.spinneret_specifications || '';
                    document.getElementById('rsCoagulationBathComposition').value = record.coagulation_bath_composition || '';
                    document.getElementById('rsCoagulationBathTemperature').value = record.coagulation_bath_temperature_c;
                    document.getElementById('rsDrawingRatio').value = record.draw_ratio;
                    document.getElementById('rsHeatTreatmentTemperature').value = record.heat_treatment_temperature_c;
                    document.getElementById('rsRemarks').value = record.remarks || '';

                    if (attachmentSection) attachmentSection.classList.remove('hidden');
                    loadResinSpinningAttachments(recordId);

                } else {
                    throw new Error(data.message || "未能加载记录。");
                }
                if (typeof hideLoading === 'function') hideLoading();
                if(modal) modal.classList.remove('hidden');
            })
            .catch(error => {
                if (typeof hideLoading === 'function') hideLoading();
                if (typeof showToast === 'function') showToast(`错误: ${error.message}`, 'error');
            });
    } else {
        modalTitle.textContent = '添加新工艺参数';
        if(modal) modal.classList.remove('hidden');
    }
}

function closeResinSpinningModal() {
    const modal = document.getElementById('resinSpinningModal');
    if(modal) modal.classList.add('hidden');
    const attachmentFileInput = document.getElementById('rsAttachmentFile');
    const attachmentFeedback = document.getElementById('rsAttachmentFeedback');
    if (attachmentFileInput) attachmentFileInput.value = '';
    if (attachmentFeedback) attachmentFeedback.textContent = '';
}

async function handleSaveResinSpinning(event) {
    event.preventDefault();
    const form = document.getElementById('resinSpinningForm');
    const recordId = document.getElementById('resinSpinningRecordId').value;

    const batchNumber = document.getElementById('rsBatchNumber').value;
    const materialGrade = document.getElementById('rsMaterialGrade').value;
    if (!batchNumber || !materialGrade) {
        if (typeof showToast === 'function') showToast('批号和材料牌号为必填项。', 'error');
        return;
    }

    const formData = {
        batch_number: batchNumber,
        material_grade: materialGrade,
        supplier: document.getElementById('rsSupplier').value || null,
        resin_type: document.getElementById('rsResinType').value || null,
        resin_molecular_weight_g_mol: parseFloat(document.getElementById('rsResinMolecularWeight').value) || null,
        polydispersity_index_pdi: parseFloat(document.getElementById('rsPolydispersityIndex').value) || null,
        intrinsic_viscosity_dl_g: parseFloat(document.getElementById('rsIntrinsicViscosity').value) || null,
        melting_point_c: parseFloat(document.getElementById('rsMeltingPoint').value) || null,
        crystallinity_percent: parseFloat(document.getElementById('rsCrystallinity').value) || null,
        spinning_method: document.getElementById('rsSpinningMethod').value || null,
        solvent_system: document.getElementById('rsSolventSystem').value || null,
        solution_concentration_percent: parseFloat(document.getElementById('rsSolutionConcentration').value) || null,
        spinning_temperature_c: parseFloat(document.getElementById('rsSpinningTemperature').value) || null,
        spinneret_specs: document.getElementById('rsSpinneretSpecs').value || null,
        coagulation_bath_composition: document.getElementById('rsCoagulationBathComposition').value || null,
        coagulation_bath_temperature_c: parseFloat(document.getElementById('rsCoagulationBathTemperature').value) || null,
        draw_ratio: parseFloat(document.getElementById('rsDrawingRatio').value) || null,
        heat_treatment_temperature_c: parseFloat(document.getElementById('rsHeatTreatmentTemperature').value) || null,
        remarks: document.getElementById('rsRemarks').value || null
    };
    // Remove null fields that were empty strings, except for required ones handled by backend
    for (const key in formData) {
        if (formData[key] === null && !(key === 'batch_number' || key === 'material_grade')) {
            // Keep null for optional numeric fields if they were truly empty and parsed to null
        } else if (typeof formData[key] === 'string' && formData[key].trim() === '' && !(key === 'batch_number' || key === 'material_grade')) {
             formData[key] = null; // Ensure empty optional strings become null
        }
    }


    const url = recordId ? `/api/resin-spinning/${recordId}` : '/api/resin-spinning';
    const method = recordId ? 'PUT' : 'POST';

    if (typeof showLoading === 'function') showLoading(true, '正在保存...');
    try {
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
            body: JSON.stringify(formData)
        });
        const responseData = await response.json();
        if (!response.ok || !responseData.success) { // Check for success flag from backend
            throw new Error(responseData.message || `保存失败: ${response.statusText}`);
        }
        if (typeof showToast === 'function') showToast(responseData.message || '保存成功!', 'success');
        closeResinSpinningModal();
        loadResinSpinningData(currentResinSpinningPage, RESIN_SPINNING_PER_PAGE, currentResinSpinningFilters);
    } catch (error) {
        console.error('Error saving resin spinning data:', error);
        if (typeof showToast === 'function') showToast(`保存失败: ${error.message}`, 'error');
    } finally {
        if (typeof hideLoading === 'function') hideLoading();
    }
}

async function deleteResinSpinningRecord(recordId) {
    if (!confirm('确定要删除这条记录吗？删除后无法恢复。')) return;

    if (typeof showLoading === 'function') showLoading(true, '正在删除...');
    try {
        const response = await fetch(`/api/resin-spinning/${recordId}`, {
            method: 'DELETE',
            headers: { 'Accept': 'application/json' }
        });
        const responseData = await response.json();
        if (!response.ok || !responseData.success) { // Check for success flag
            throw new Error(responseData.message || '删除失败');
        }
        if (typeof showToast === 'function') showToast(responseData.message || '删除成功!', 'success');
        loadResinSpinningData(1, RESIN_SPINNING_PER_PAGE, {}); // Reset to first page after delete
    } catch (error) {
        console.error('Error deleting resin spinning record:', error);
        if (typeof showToast === 'function') showToast(`删除失败: ${error.message}`, 'error');
    } finally {
        if (typeof hideLoading === 'function') hideLoading();
    }
}


function initializeResinSpinningModuleEventListeners() {
    // Main actions
    document.getElementById('addResinSpinningBtn')?.addEventListener('click', () => openResinSpinningModal());
    document.getElementById('refreshResinSpinningBtn')?.addEventListener('click', () => loadResinSpinningData(currentResinSpinningPage, RESIN_SPINNING_PER_PAGE, currentResinSpinningFilters));
    document.getElementById('downloadResinSpinningTemplateBtn')?.addEventListener('click', () => { 
        // Use a placeholder path for the template. In a real scenario, this would be a static file served by Flask.
        // For this task, as we created a .txt file, we'll link to that.
        window.location.href = '/assets/templates/resin_spinning_template_headers.txt'; 
    });
    document.getElementById('batchImportResinSpinningBtn')?.addEventListener('click', () => { 
        openResinSpinningImportModal(); 
    });
    
    // Search
    document.getElementById('searchResinSpinningBtn')?.addEventListener('click', () => {
        const filters = {
            batch_number: document.getElementById('searchBatchNumberRS').value,
            material_grade: document.getElementById('searchMaterialGradeRS').value
        };
        loadResinSpinningData(1, RESIN_SPINNING_PER_PAGE, filters);
    });
    document.getElementById('clearSearchResinSpinningBtn')?.addEventListener('click', () => {
        document.getElementById('searchBatchNumberRS').value = '';
        document.getElementById('searchMaterialGradeRS').value = '';
        loadResinSpinningData(1, RESIN_SPINNING_PER_PAGE, {});
    });

    // Modal form (Add/Edit)
    document.getElementById('resinSpinningForm')?.addEventListener('submit', handleSaveResinSpinning);
    document.getElementById('closeResinSpinningModalBtn')?.addEventListener('click', closeResinSpinningModal);
    document.getElementById('cancelResinSpinningFormBtn')?.addEventListener('click', closeResinSpinningModal);

    // Import Modal
    document.getElementById('closeResinSpinningImportModalBtn')?.addEventListener('click', closeResinSpinningImportModal);
    document.getElementById('uploadResinSpinningImportBtn')?.addEventListener('click', handleResinSpinningFileUpload);

    // Import Modal
    document.getElementById('closeResinSpinningImportModalBtn')?.addEventListener('click', closeResinSpinningImportModal);
    document.getElementById('uploadResinSpinningImportBtn')?.addEventListener('click', handleResinSpinningFileUpload);

    // Table actions (event delegation)
    document.getElementById('resinSpinningTableBody')?.addEventListener('click', function(event) {
        const target = event.target;
        if (target.classList.contains('edit-rs-btn')) {
            openResinSpinningModal(target.dataset.id);
        } else if (target.classList.contains('delete-rs-btn')) {
            deleteResinSpinningRecord(target.dataset.id);
        }
    });
    
    // Batch import (placeholder for now)
    // Batch import button inside main module view (already handled above, this is a duplicate from prompt)
    // document.getElementById('batchImportResinSpinningBtn')?.addEventListener('click', () => {
    //     if(typeof showToast === 'function') showToast('批量导入功能将在后续步骤中实现。', 'info');
    // });
}

function openResinSpinningImportModal() {
    const modal = document.getElementById('resinSpinningBatchImportModal');
    const feedbackDiv = document.getElementById('resinSpinningImportFeedback');
    const fileInput = document.getElementById('resinSpinningImportFile');
    if(fileInput) fileInput.value = ''; // Clear previous file selection
    if(feedbackDiv) feedbackDiv.innerHTML = ''; // Clear previous feedback
    if(modal) modal.classList.remove('hidden');
}

function closeResinSpinningImportModal() {
    const modal = document.getElementById('resinSpinningBatchImportModal');
    if(modal) modal.classList.add('hidden');
}

async function handleResinSpinningFileUpload() {
    const fileInput = document.getElementById('resinSpinningImportFile');
    const feedbackDiv = document.getElementById('resinSpinningImportFeedback');
    
    if (!fileInput || !feedbackDiv) {
        console.error("Import modal elements not found.");
        return;
    }
    feedbackDiv.innerHTML = ''; // Clear previous feedback

    const file = fileInput.files[0];
    if (!file) {
        feedbackDiv.innerHTML = '<p class="text-red-500">请先选择一个文件。</p>';
        return;
    }

    const allowedTypes = ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel'];
    if (!allowedTypes.includes(file.type)) {
        feedbackDiv.innerHTML = '<p class="text-red-500">文件类型无效。请上传 .xlsx 或 .xls 文件。</p>';
        return;
    }

    if (typeof showLoading === 'function') showLoading(true, '正在上传和处理文件...');
    
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/api/resin-spinning/batch-import', {
            method: 'POST',
            body: formData,
            // 'Content-Type': 'multipart/form-data' is set automatically by browser for FormData
            headers: { 'Accept': 'application/json' } // Expect JSON response
        });

        const result = await response.json();

        if (!response.ok) { // Handles HTTP errors like 400, 500 from backend before service logic
            throw new Error(result.message || `文件上传失败 (状态码: ${response.status})`);
        }
        
        // Backend returns details about success/failure counts
        let feedbackHTML = `<p class="font-semibold">导入结果:</p>`;
        feedbackHTML += `<p class="text-green-600">成功导入 ${result.details.success_count} 条记录。</p>`;
        if (result.details.failure_count > 0) {
            feedbackHTML += `<p class="text-red-600">导入失败 ${result.details.failure_count} 条记录。</p>`;
            if (result.details.errors && result.details.errors.length > 0) {
                feedbackHTML += '<p class="font-semibold mt-2">错误详情:</p><ul class="list-disc list-inside max-h-40 overflow-y-auto">';
                result.details.errors.forEach(err => {
                    feedbackHTML += `<li class="text-red-500 text-xs">行 ${err.row_number}: ${err.error} (数据: ${JSON.stringify(err.data).substring(0,100)}...)</li>`;
                });
                feedbackHTML += '</ul>';
            }
        } else {
             feedbackHTML += '<p class="text-green-600">所有记录均已成功导入！</p>';
        }
        feedbackDiv.innerHTML = feedbackHTML;

        if (result.details.success_count > 0) {
            loadResinSpinningData(1, RESIN_SPINNING_PER_PAGE, {}); // Refresh table to show new data
            // Optionally close modal if all successful after a delay
            if (result.details.failure_count === 0) {
                setTimeout(closeResinSpinningImportModal, 2000);
            }
        }

    } catch (error) {
        console.error('Error during file upload:', error);
        feedbackDiv.innerHTML = `<p class="text-red-500">上传或处理失败: ${error.message}</p>`;
        if (typeof showToast === 'function') showToast(`上传失败: ${error.message}`, 'error');
    } finally {
        if (typeof hideLoading === 'function') hideLoading();
    }
}


// This function will be called from index.html's activateModule
// It assumes 'contentArea' is the ID of the main content div in index.html
function renderResinSpinningModuleView(targetContentAreaElement) {
    if (!targetContentAreaElement) {
        console.error('Target content area not provided for Resin Spinning module.');
        return;
    }
    targetContentAreaElement.innerHTML = getResinSpinningModuleHTML();
    // Add specific styles for this module if needed, or ensure they are in main CSS
    const tempStyle = document.createElement('style');
    tempStyle.id = 'resin-spinning-module-styles'; // Avoid conflict with other temp styles
    tempStyle.textContent = `
        .form-input { @apply mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm; }
        .form-label { @apply block text-sm font-medium text-gray-700; }
    `;
    // Remove old style if it exists to prevent duplication
    const oldStyle = document.getElementById(tempStyle.id);
    if (oldStyle) oldStyle.remove();
    document.head.appendChild(tempStyle);

    initializeResinSpinningModuleEventListeners();
    loadResinSpinningData(1, RESIN_SPINNING_PER_PAGE, {}); // Load initial data
}

// Make the main rendering function available if needed globally or for module systems
// window.renderResinSpinningModuleView = renderResinSpinningModuleView;

console.log('resin_spinning_module.js loaded'); // For debugging

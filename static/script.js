document.addEventListener('DOMContentLoaded', function () {
    // --- SELECTORS ---
    const tabButtons = document.querySelectorAll('.top-bar .tab-button');
    const tabContents = document.querySelectorAll('.main-content .tab-content');
    const uploadNewBtn = document.querySelector('.btn-upload-new');
    const uploadForm = document.getElementById('upload-form');
    const documentsTableBody = document.getElementById('documents-table-body');
    const processedFilesDropdown = document.getElementById('processed-files-dropdown');
    const jsonFormContainer = document.getElementById('json-form-container');
    const saveProgressBtn = document.getElementById('save-progress-btn');
    const markCompleteBtn = document.getElementById('mark-complete-btn');
    const downloadReportBtn = document.getElementById('download-report-btn');
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const backToLibraryLink = document.getElementById('back-to-library-link');
    const uploadSubmitBtn = document.getElementById('upload-submit-btn');
    const formAndButtonsContainer = document.getElementById('form-and-buttons-container');

    // --- DRAG & DROP LOGIC ---
    if (dropZone && fileInput) {
        // Make the whole zone clickable to open file dialog
        dropZone.addEventListener('click', () => fileInput.click());

        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, preventDefaults, false);
            document.body.addEventListener(eventName, preventDefaults, false);
        });

        // Highlight drop zone when item is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => dropZone.classList.add('drag-over'), false);
        });

        // Un-highlight drop zone when item leaves or is dropped
        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => dropZone.classList.remove('drag-over'), false);
        });

        // Handle dropped files
        dropZone.addEventListener('drop', handleDrop, false);

        // Update text when a file is selected via the browse button
        fileInput.addEventListener('change', () => {
            if (fileInput.files.length > 0) {
                updateDropZoneText(fileInput.files[0].name);
                uploadSubmitBtn.disabled = false;
            }
        });
    }

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;

        if (files.length > 0) {
            fileInput.files = files; // Assign dropped files to the input
            updateDropZoneText(files[0].name);
            uploadSubmitBtn.disabled = false;
        }
    }

    function resetUploadForm() {
        uploadForm.reset();
        if (uploadSubmitBtn) uploadSubmitBtn.disabled = true;
        const p = dropZone.querySelector('p');
        if (p) {
            p.innerHTML = `Drag & drop a PDF file here or <a href="#" class="text-blue-500" onclick="document.getElementById('file-input').click(); return false;">click to browse</a>.`;
        }
    }

    function updateDropZoneText(fileName) {
        const p = dropZone.querySelector('p');
        if (p) {
            p.innerHTML = `File selected: <span class="font-semibold">${fileName}</span>. Not the right file? <a href="#" class="text-blue-500" onclick="document.getElementById('file-input').click(); return false;">Change</a>.`;
        }
    }

    // --- INITIALIZATION ---
    loadDocuments();

    // --- CORE FUNCTIONS ---

    window.deleteDocument = async function(filename) {


        try {
            const response = await fetch(`/delete_document/${filename}`, {
                method: 'DELETE',
            });

            const result = await response.json();

            if (response.ok) {
                alert(result.message);
                loadDocuments(); // Refresh the document list
            } else {
                throw new Error(result.error || 'Failed to delete document.');
            }
        } catch (error) {
            console.error('Error deleting document:', error);
            alert(error.message);
        }
    }

    async function loadDocuments() {
        try {
            const response = await fetch('/get_documents');
            const documents = await response.json();
            documentsTableBody.innerHTML = '';
            document.getElementById('total-docs').textContent = documents.length; // Update total documents count

            const finishedDocuments = documents.filter(doc => doc.status === 'verified');
            document.getElementById('finished-docs').textContent = finishedDocuments.length; // Update finished documents count

            const uploadedDocuments = documents.filter(doc => doc.status === 'uploaded');
            document.getElementById('awaiting-verification').textContent = uploadedDocuments.length; // Update awaiting verification count

            const inProgressDocuments = documents.filter(doc => doc.status === 'in_progress');
            document.getElementById('being-analyzed').textContent = inProgressDocuments.length; // Update being analyzed count

            if (documents.error) {
                throw new Error(documents.error);
            }
            if (documents.length === 0) {
                documentsTableBody.innerHTML = '<tr><td colspan="8" class="text-center">No documents found.</td></tr>';
            } else {
                documents.forEach(doc => {
                    const row = document.createElement('tr');
                    
                    // Determine status badge classes
                    let statusClasses = '';
                    let statusText = doc.status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                    if (doc.status === 'uploaded') {
                        statusClasses = 'bg-gray-200 text-gray-800';
                    } else if (doc.status === 'in_progress') {
                        statusClasses = 'bg-yellow-200 text-yellow-800';
                    } else if (doc.status === 'verified') {
                        statusClasses = 'bg-green-200 text-green-800';
                    }

                    row.innerHTML = `
                        <td>${doc.custom_name || doc.filename}</td>
                        <td>${doc.external_id || 'N/A'}</td>
                        <td>${doc.tenant_code || 'N/A'}</td>
                        <td>${doc.property_no || 'N/A'}</td>
                        <td>${doc.action || 'N/A'}</td>
                        <td>${new Date(doc.upload_date).toLocaleDateString()}</td>
                        <td><span class="px-2 py-1 rounded-full text-xs font-medium ${statusClasses}">${statusText}</span></td>
                        <td class="actions-cell">
                            <button class="action-btn" onclick="viewDocument('${doc.filename}')">View</button>
                            <button class="action-btn delete-btn delete-document-btn" data-filename="${doc.filename}"><i class="fas fa-trash-alt"></i></button>
                        </td>
                    `;
                    documentsTableBody.appendChild(row);

                    const deleteButton = row.querySelector('.delete-document-btn');
                    if (deleteButton) {
                        deleteButton.addEventListener('click', function() {
                            const filename = this.dataset.filename;
                            window.deleteDocument(filename);
                        });
                    }
                });
            }
        } catch (error) {
            console.error('Failed to load documents:', error);
            documentsTableBody.innerHTML = '<tr><td colspan="8" class="text-center">Failed to load documents.</td></tr>';
        }
    }

    async function loadProcessedFiles() {
        try {
            const response = await fetch('/get_processed_files');
            const files = await response.json();
            processedFilesDropdown.innerHTML = '<option value="">-- Select a file --</option>';
            if (files.error) {
                throw new Error(files.error);
            }
            files.forEach(file => {
                const option = document.createElement('option');
                option.value = file;
                option.textContent = file;
                processedFilesDropdown.appendChild(option);
            });
        } catch (error) {
            console.error('Failed to load processed files:', error);
        }
    }

    function switchTab(tabId) {
        tabContents.forEach(content => {
            if (content.id === tabId) {
                content.classList.remove('hidden');
            } else {
                content.classList.add('hidden');
                // If switching away from generate-tab, clear the form and reset dropdown
                if (content.id === 'generate-tab') {
                    jsonFormContainer.innerHTML = '';
                    formAndButtonsContainer.classList.add('hidden');
                    if (processedFilesDropdown) {
                        processedFilesDropdown.value = ''; // Reset dropdown to default
                    }
                }
            }
        });

        tabButtons.forEach(button => {
            if (button.dataset.tab === tabId) {
                button.classList.add('active');
            } else {
                button.classList.remove('active');
            }
        });

        // Load documents or processed files based on the active tab
        if (tabId === 'summary-tab') {
            loadDocuments();
        } else if (tabId === 'generate-tab') {
            loadProcessedFiles(); // Ensure dropdown is populated when generate tab is active
        }
    }

    function showToast(message, duration, type = 'saving') {
        const toast = document.getElementById('toast-notification');
        toast.textContent = message;
        toast.classList.remove('success', 'saving'); // Remove previous type classes

        if (type === 'success') {
            toast.classList.add('success');
        } else {
            toast.classList.add('saving');
        }

        toast.classList.add('show');
        setTimeout(() => {
            toast.classList.remove('show');
        }, duration);
    }

    // Event listener for the Save Progress button
    if (saveProgressBtn) {
        saveProgressBtn.addEventListener('click', () => {
            showToast('Saving...', 750, 'saving'); // Show 'Saving...' for 0.75 seconds
            setTimeout(() => {
                showToast('Saved successfully!', 1000, 'success'); // Show 'Saved successfully!' for 1 second after 'Saving...' disappears
            }, 750); // Delay for 0.75 seconds before showing the next toast
        });
    }

    // --- FORM BUILDER --- 
    function createInputField(container, key, value, fullKey) {
        const formGroup = document.createElement('div');
        formGroup.className = 'mb-4';
    const parentFieldsetsToHideName = ['property_insurance', 'workers_compensation', 'umbrella_liability', 'automobile_liability', 'commercial_general_liability'];
    if (key === 'name' && parentFieldsetsToHideName.some(fieldset => fullKey.startsWith(fieldset))) {
        formGroup.classList.add('hidden');
    }
        const label = document.createElement('label');
        label.className = 'block text-xs text-gray-700 capitalize';
        label.textContent = key.replace(/_/g, ' ');

        let input;
        if (key === 'notice_of_cancellation' || key === 'description_of_operations') {
            input = document.createElement('textarea');
            input.rows = 3; // Initial height for textarea
        } else {
            input = document.createElement('input');
            input.type = 'text';
        }
        input.name = fullKey;
        input.value = value;
        input.className = 'mt-1 block w-full p-1 border border-gray-300 rounded-md shadow-sm text-sm';

        if (input.tagName === 'TEXTAREA') {
            input.style.overflowY = 'hidden'; // Hide scrollbar
            input.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = (this.scrollHeight) + 'px';
            });

        }
        formGroup.appendChild(label);
        formGroup.appendChild(input);

        if (input.tagName === 'TEXTAREA') {
            // Set initial height after appending to ensure scrollHeight is accurate
            setTimeout(() => {
                input.style.height = 'auto';
                input.style.height = (input.scrollHeight) + 'px';
            }, 0);
        }
        // container.appendChild(formGroup); // Remove this line
        return formGroup; // Add this line
    }

    function buildForm(data, container, prefix = '') {
        if (prefix === '') {
            container.innerHTML = '';
        }

        const isTopLevelArray = Array.isArray(data) && prefix === '';
        const twoColumnInsuranceTypes = [
            'commercial_general_liability',
            'automobile_liability',
            'umbrella_liability',
            'workers_compensation',
            'property_insurance'
        ];

        if (isTopLevelArray) {
            data.forEach((item, index) => {
                const card = document.createElement('div');
                card.className = 'bg-gray-800 p-6 rounded-lg shadow-lg mb-6';
                const title = document.createElement('h3');
                title.className = 'text-xl font-bold text-white mb-4 capitalize border-b border-gray-700 pb-2';
                
                const nameKey = Object.keys(item).find(k => k.toLowerCase().includes('name'));
                const titleText = nameKey ? item[nameKey] : `Item ${index + 1}`;
                title.textContent = titleText;

                card.appendChild(title);
                buildForm(item, card, `${prefix}[${index}]`);
                container.appendChild(card);
            });
        } else if (typeof data === 'object' && data !== null && !Array.isArray(data)) {
            let twoColumnLayoutContainer = null;
            let rightColumnContainer = null;

            if (twoColumnInsuranceTypes.includes(prefix)) {
                twoColumnLayoutContainer = document.createElement('div');
                twoColumnLayoutContainer.className = 'grid grid-cols-1 md:grid-cols-2 gap-4';
                container.appendChild(twoColumnLayoutContainer);

                rightColumnContainer = document.createElement('div');
            }

            for (const key in data) {
                const fullKey = prefix ? `${prefix}.${key}` : key;
                const value = data[key];

                if (typeof value === 'object' && value !== null) {
                    const fieldset = document.createElement('fieldset');
                    fieldset.className = 'mb-4 p-4 border border-gray-700 rounded bg-white shadow-md';
                    const legend = document.createElement('legend');
                    legend.className = 'font-bold text-gray-900 px-2 capitalize';
                    legend.textContent = key.replace(/_/g, ' ');
                    fieldset.appendChild(legend);
                    buildForm(value, fieldset, fullKey);

                    // Existing logic for producer/insured
                    if (key === 'producer' || key === 'insured') {
                        let twoColumnContainer = container.querySelector('.producer-insured-container');
                        if (!twoColumnContainer) {
                            twoColumnContainer = document.createElement('div');
                            twoColumnContainer.className = 'grid grid-cols-1 md:grid-cols-2 gap-4';
                            twoColumnContainer.classList.add('producer-insured-container');
                            container.appendChild(twoColumnContainer);
                        }
                        twoColumnContainer.appendChild(fieldset);
                    } else if (key === 'effective_date' && !twoColumnInsuranceTypes.includes(prefix)) {
                        container.prepend(fieldset);
                    } else if (key === 'effective_date' && twoColumnInsuranceTypes.includes(prefix)) {
                        fieldset.className = 'p-4 border border-gray-700 rounded bg-white shadow-md'; // Removed mb-4
                        twoColumnLayoutContainer.appendChild(fieldset);
                    }
                    else {
                        container.appendChild(fieldset);
                    }
                } else {
                    const inputField = createInputField(container, key, value, fullKey); // createInputField returns the formGroup div
                    // Define specific fields for the right column for each insurance type
                    const insuranceTypeRightColumnFields = {
                        'commercial_general_liability': ['policy_number', 'insurer_name', 'claims_basis'],
                        'automobile_liability': ['policy_number', 'insurer_name', 'coverage_type'],
                        'umbrella_liability': ['policy_number', 'insurer_name', 'claims_basis'],
                        'workers_compensation': ['policy_number', 'insurer_name'],
                        'property_insurance': ['policy_number', 'insurer_name', 'insurer'] // Added 'insurer' here
                    };

                    // Check if the current prefix (insurance type) is in the twoColumnInsuranceTypes list
                    // and if the current key (field) is in the specific right column fields for this insurance type
                    if (twoColumnInsuranceTypes.includes(prefix) && insuranceTypeRightColumnFields[prefix] && insuranceTypeRightColumnFields[prefix].includes(key)) {
                        rightColumnContainer.appendChild(inputField);
                    } else {
                        container.appendChild(inputField);
                    }
                }
            }
            if (twoColumnInsuranceTypes.includes(prefix) && rightColumnContainer) {
                twoColumnLayoutContainer.prepend(rightColumnContainer);
            }

        } else if (Array.isArray(data)) {
             data.forEach((item, index) => {
                const itemPrefix = `${prefix}[${index}]`;
                if (typeof item === 'object' && item !== null) {
                    const itemFieldset = document.createElement('fieldset');
                    itemFieldset.className = 'mb-2 p-2 border border-gray-700 rounded';
                    const itemLegend = document.createElement('legend');
                    itemLegend.className = 'font-semibold text-gray-500 px-2';
                    itemLegend.textContent = `Item ${index + 1}`;
                    itemFieldset.appendChild(itemLegend);
                    buildForm(item, itemFieldset, itemPrefix);
                    container.appendChild(itemFieldset); 
                } else {
                    createInputField(container, `${prefix}[${index}]`, item, itemPrefix);
                }
            });
        }
    }

    function getJsonFromForm(form) {
        const formData = new FormData(form);
        const json = {}
        // This is a simplified reconstruction. A full implementation
        // would need to handle nested objects and arrays correctly based on input names.
        for (const [key, value] of formData.entries()) {
             // Basic dot notation to object conversion
            const keys = key.replace(/\d+/g, '.$1').split('.');
            keys.reduce((acc, current, index) => {
                if (index === keys.length - 1) {
                    return acc[current] = value;
                }
                if (!acc[current]) {
                    acc[current] = isNaN(keys[index+1]) ? {} : [];
                }
                return acc[current];
            }, json);
        }
        return json;
    }

    // --- EVENT LISTENERS ---
    backToLibraryLink?.addEventListener('click', (e) => {
        e.preventDefault();
        switchTab('summary-tab');
    });

    tabButtons.forEach(button => button.addEventListener('click', () => switchTab(button.dataset.tab)));
    uploadNewBtn?.addEventListener('click', () => switchTab('upload-tab'));

    uploadForm?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(uploadForm);
        if (!formData.get('file')?.size) {
            alert('Please select a file.');
            return;
        }

        const submitBtn = document.getElementById('upload-submit-btn');
        const originalBtnContent = submitBtn.innerHTML;
        let response; // Declare response here to make it accessible in finally block

        // Disable button and show spinner
        submitBtn.disabled = true;
        submitBtn.innerHTML = `
            <div class="flex items-center justify-center">
                <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>Uploading...</span>
            </div>
        `;

        try {
            const response = await fetch('/upload', { method: 'POST', body: formData });
            const data = await response.json();
            if (data.error) throw new Error(data.error);
            alert('File uploaded and processed successfully!');
            resetUploadForm();
            loadDocuments();
            switchTab('summary-tab');
        } catch (error) {
            console.error('Upload failed:', error);
            alert(`Upload failed: ${error.message}`);
        } finally {
            // Restore original button content
            submitBtn.innerHTML = originalBtnContent;
            // The resetUploadForm function will handle re-disabling the button on success.
            // If the upload failed (response is falsy or not ok), re-enable the button.
            if (!response || !response.ok) {
                 submitBtn.disabled = false;
            }
        }
    });

    processedFilesDropdown?.addEventListener('change', async () => {
        const selectedFile = processedFilesDropdown.value;

        if (selectedFile) {
            // A file is selected, so show the container and fetch the form data
            formAndButtonsContainer.classList.remove('hidden');
            jsonFormContainer.innerHTML = '<p class="text-center">Loading form...</p>'; // Show a loading message
            try {
                const response = await fetch(`/get_json/${selectedFile}`);
                const data = await response.json();
                if (data.error) throw new Error(data.error);
                jsonFormContainer.innerHTML = ''; // Clear loading message
                buildForm(data, jsonFormContainer);
            } catch (error) {
                console.error('Failed to fetch JSON:', error);
                jsonFormContainer.textContent = 'Failed to load content.';
            }
        } else {
            // No file is selected, so hide the container and clear the form
            formAndButtonsContainer.classList.add('hidden');
            jsonFormContainer.innerHTML = '';
        }
    });


    // Event listener for Save Progress button
    saveProgressBtn?.addEventListener('click', async function() {
        const processedFilesDropdown = document.getElementById('processed-files-dropdown');
        const currentFilename = processedFilesDropdown.value;
        if (currentFilename) {
            try {
                // Assuming you have the current JSON data from the form
                const currentJsonData = getJsonFromForm(jsonFormContainer); // You might need to adjust this based on your form structure
                console.log('JSON data to be sent:', currentJsonData);

                const response = await fetch(`/save_json/${currentFilename}`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(currentJsonData)
                });
                if (response.ok) {
                    console.log('Document status updated to in_progress');
                    loadDocuments(); // Refresh table
                } else {
                    console.error('Failed to update status:', await response.text());
                }
            } catch (error) {
                console.error('Error saving JSON:', error);
            }
        } else {
            alert('Please select a file to save progress for.');
        }
    });

    // Event listener for Mark as Complete button
    markCompleteBtn?.addEventListener('click', async function() {
        const processedFilesDropdown = document.getElementById('processed-files-dropdown');
        const currentFilename = processedFilesDropdown.value;
        if (currentFilename) {
            try {
                const response = await fetch(`/mark_complete/${currentFilename}`, {
                    method: 'POST',
                });
                if (response.ok) {
                    showToast('Marked as Verified!', 2000, 'success');
                    console.log('Document status updated to verified');
                    loadDocuments(); // Refresh table
                } else {
                    console.error('Failed to update status:', await response.text());
                }
            } catch (error) {
                console.error('Error marking complete:', error);
            }
        }
    });

    // Event listener for Download Report button
    downloadReportBtn?.addEventListener('click', function() {
        const currentFilename = processedFilesDropdown.value;
        if (currentFilename) {
            window.open(`/download_pdf/${currentFilename}`);
        } else {
            alert('Please select a file to download the report for.');
        }
    });
});
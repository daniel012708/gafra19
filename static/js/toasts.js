;(function(){
  'use strict';

  function ensureContainer(){
    let container = document.getElementById('toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      container.className = 'toast-container-custom';
      document.body.appendChild(container);
    }
    return container;
  }

  function createToast(message, type, delay){
    const container = ensureContainer();
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-bg-${type} border-0 mb-2`;
    toast.setAttribute('role','alert');
    toast.setAttribute('aria-live','assertive');
    toast.setAttribute('aria-atomic','true');
    // escape message safely - caller should pass text; keep simple here
    const body = document.createElement('div');
    body.className = 'd-flex';
    body.innerHTML = `<div class="toast-body">${String(message)}</div><button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>`;
    toast.appendChild(body);
    container.appendChild(toast);

    try {
      const bs = new bootstrap.Toast(toast, { delay: delay || 4000 });
      toast.addEventListener('hidden.bs.toast', function(){ toast.remove(); });
      bs.show();
    } catch(e) {
      // fallback: remove after timeout
      setTimeout(()=>{ toast.remove(); }, delay || 4000);
    }
    return toast;
  }

  window.showToast = function(message, type='primary', delay=4000){
    return createToast(message, type, delay);
  };
  window.toastSuccess = function(msg, delay){ return window.showToast(msg, 'success', delay); };
  window.toastError = function(msg, delay){ return window.showToast(msg, 'danger', delay); };
  window.toastInfo = function(msg, delay){ return window.showToast(msg, 'info', delay); };

})();

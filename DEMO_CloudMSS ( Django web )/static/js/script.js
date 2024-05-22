
function input_box() {

    var countInput = document.getElementById("num");
    var count = parseInt(countInput.value); // 獲取輸入框中的數字

    // 檢查输入是否為有效数字
    if (!isNaN(count) && count > 0) {

        // 顯示步驟二
        document.getElementById("step_2").style.display = "block";

        var textareaContainer = document.getElementById("textarea-container");
        textareaContainer.textContent = "";

        // 讀取圖標 URL
        var iconUrl = document.getElementById("icon").getAttribute("data-icon-url");
        
        // 生成指定數量的文本框
        for (var i = 0; i < count; i++) {

            var container = document.createElement("div");
            container.classList.add("textarea-container");

            // 創建圖標元素
            var icon = document.createElement("img");
            icon.src = iconUrl;             // 設置圖標的 URL
            icon.alt = "icon";              // 設置圖標的替代文本
            icon.classList.add("icon_client");     // 添加樣式類別

            var textarea_K = document.createElement("textarea");
            textarea_K.rows = 5;          // 設置文本區域的行数
            textarea_K.cols = 40;         // 設置文本區域的列数
            textarea_K.name = "textarea_K_" + i.toString();
            textarea_K.classList.add("new_textarea");     // 添加樣式類別

            var textarea_t = document.createElement("textarea");
            textarea_t.rows = 5;          // 設置文本區域的行数
            textarea_t.cols = 40;         // 設置文本區域的列数
            textarea_t.name = "textarea_t_" + i.toString();
            textarea_t.classList.add("new_textarea");     // 添加樣式類別

            // 將圖標元素添加到容器中
            container.appendChild(icon);

            // 將 textarea 添加到容器中
            container.appendChild(textarea_K);

            // 將 textarea 添加到容器中
            container.appendChild(textarea_t);

            // 將容器添加到文档中
            textareaContainer.appendChild(container);
        }

        // 顯示提交按钮
        document.getElementById("submit-btn").style.display = "block";

    } else {
        alert("Please enter a valid number greater than 0.");
    }
}

function getSelectedClientsText() {

    var selectedClients = document.querySelectorAll('input[type="checkbox"]:checked');

    var client_text = [];

    selectedClients.forEach(function(checkbox) {
        var text = checkbox.nextElementSibling.querySelector('.client_text').textContent.trim();
        client_text.push(text);
    });

    document.getElementById('selected_clients_text').value = "[" + client_text.toString() + "]";

    return true; // 繼續提交表單
}

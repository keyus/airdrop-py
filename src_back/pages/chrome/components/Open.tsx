import { Dropdown,  } from 'antd'
import Chromeicon from '@/assets/chrome.svg?react'



type Props = {
    selectedRows: any[]
    onOk: () => void
}

export default function Open(props: Props) {
    const { selectedRows, onOk } = props

    const onOpenChrome = async () => {
        const names = selectedRows.map(it => it.name)
        await globalThis.window.pywebview.api.open_chrome(names)
        window.message.success('chrome,打开成功')
        onOk()
    }

    const onOpenTelegram = async () => {
        const names = selectedRows.map(it => it.name)
        await globalThis.window.pywebview.api.open_tg(names)
        window.message.success('telegram,打开成功')
        onOk()
    }

    return (
        <Dropdown.Button
            size='large'
            disabled={selectedRows.length === 0}
            menu={{
                items: [
                    {
                        label: '启动 Telegram',
                        key: '1',
                        onClick: onOpenTelegram
                    },
                ]
            }}
            onClick={onOpenChrome}>
            <Chromeicon width={16} height={16} /> 启动 chrome
        </Dropdown.Button>
    )
}

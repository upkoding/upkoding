import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import id from 'dayjs/locale/id'

dayjs.locale(id)
dayjs.extend(relativeTime);

export default dayjs
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>

#define DEFAULT_TIMEBANK      10000
#define DEFAULT_TIME_PER_MOVE 100
#define LEV_LIMIT 5

enum ID{ EMPTY = 0, ID0 = 1, ID1 = 2, };
enum win_map_state{ UNKNOWN = 0, ID0_WIN = 1, ID1_WIN = 2, DRAW_FULL = 3 };
enum score{ SC_INVALID = -(1<<24), SC_ZERO = 0, SC_WIN = 1<<16};
char win_map[1 << 18];
int field_pos_map[9][9];
int field_off_map[9][9];
int field_off_map_set[9][9][4];
int field_off_map_clear[9][9];
int field[10];

#define MSG(fmt, ...) fprintf(stderr, "DEBUG: " fmt, __VA_ARGS__)
#define OP_ID(id) (3-(id))
#define FIELD_ALL 9
#define SET(x, y, id) field[field_pos_map[y][x]] |= field_off_map_set[y][x][id]
#define CLEAR(x, y)   field[field_pos_map[y][x]] &= field_off_map_clear[y][x]
#define IS_VALID(x, y) ((field[field_pos_map[y][x]] | field_off_map_clear[y][x])==field_off_map_clear[y][x] && win_map[field[field_pos_map[y][x]]] == UNKNOWN)
#define GET_POS_ID(N, x, y) ((N >> 2*(y*3+x)) & 0x03)
#define GET_STATE(pos) win_map[field[pos]]
#define GET_STATE_XY(x, y) win_map[field[field_pos_map[y][x]]]
#define UPDATE_FIELD_ALL() do{int _;field[FIELD_ALL]=0;for(_=0;_<9;_++){field[FIELD_ALL] |= GET_STATE(_) << 2*_;}}while(0)


typedef struct {
	int *field;
	int cal_level;
	int id;
	int score;
	int x, y;
} ginfo_t;
ginfo_t ginfo = {
	field,
};
int get_res(ginfo_t * ginfo, int id);
void init_maps(void){
	int n,i,j,id;
	for(j=0;j<9;j++){
		for(i=0;i<9;i++){
			field_pos_map[j][i] = (j/3)*3 + i/3;
			field_off_map[j][i] =((j%3)*3 + i%3) * 2;
 			field_off_map_clear[j][i] = ~(0x03 << ((j%3)*3 + (i%3)) * 2);
 			for(id=1;id<=2;id++) field_off_map_set[j][i][id] = id << ((j%3)*3 + (i%3)) * 2;
		}
	}
	// init win map
	for(n=0;n<(1 << 18);n++){
		#define _GPI(N, x, y) GET_POS_ID(N, x, y)
		if((_GPI(n, 0, 0) == ID0 || _GPI(n, 0, 0) == ID1) && ((_GPI(n, 0, 0) == _GPI(n, 1, 0) && _GPI(n, 1, 0) == _GPI(n, 2, 0)) || (_GPI(n, 0, 0) == _GPI(n, 0, 1) && _GPI(n, 0, 1) == _GPI(n, 0, 2)))){win_map[n] = _GPI(n, 0, 0);}
		else if((_GPI(n, 1, 1) == ID0 || _GPI(n, 1, 1) == ID1) && (
				(_GPI(n, 0, 1) == _GPI(n, 1, 1) && _GPI(n, 1, 1) == _GPI(n, 2, 1)) || (_GPI(n, 1, 0) == _GPI(n, 1, 1) && _GPI(n, 1, 1) == _GPI(n, 1, 2)) ||
				(_GPI(n, 0, 0) == _GPI(n, 1, 1) && _GPI(n, 1, 1) == _GPI(n, 2, 2)) || (_GPI(n, 0, 2) == _GPI(n, 1, 1) && _GPI(n, 1, 1) == _GPI(n, 2, 0)))){win_map[n] = _GPI(n, 1, 1);}
		else if((_GPI(n, 2, 2) == ID0 || _GPI(n, 2, 2) == ID1) && ((_GPI(n, 0, 2) == _GPI(n, 1, 2) && _GPI(n, 1, 2) == _GPI(n, 2, 2)) || (_GPI(n, 2, 0) == _GPI(n, 2, 1) && _GPI(n, 2, 1) == _GPI(n, 2, 2)))){win_map[n] = _GPI(n, 2, 2);}
		else if((_GPI(n, 0, 0) != UNKNOWN) && (_GPI(n, 0, 1) != UNKNOWN) && (_GPI(n, 0, 2) != UNKNOWN) &&
			 (_GPI(n, 1, 0) != UNKNOWN) && (_GPI(n, 1, 1) != UNKNOWN) && (_GPI(n, 1, 2) != UNKNOWN) &&
			 (_GPI(n, 2, 0) != UNKNOWN) && (_GPI(n, 2, 1) != UNKNOWN) && (_GPI(n, 2, 2) != UNKNOWN)){win_map[n] = DRAW_FULL;}
		else{win_map[n] = UNKNOWN;}
	}
}

void round_init0(ginfo_t * ginfo){
	static int validActionCount, row, col;
    scanf("%d%d", &ginfo->y, &ginfo->x);
    scanf("%d", &validActionCount);
    for (int i = 0; i < validActionCount; i++) { scanf("%d%d", &row, &col); }
	ginfo->score = SC_INVALID;
	ginfo->id = ID0;
	if(ginfo->x >= 0 && ginfo->y >= 0){ SET(ginfo->x, ginfo->y, ID1); get_res(ginfo, ID0);}
	else{ ginfo->x = 4; ginfo->y = 4; }
}

void round_init(ginfo_t * ginfo){
	static int validActionCount, row, col;
    scanf("%d%d", &ginfo->y, &ginfo->x);
//	MSG("SET(%d, %d, ID1);\n", ginfo->x, ginfo->y);
    scanf("%d", &validActionCount);
    for (int i = 0; i < validActionCount; i++) { scanf("%d%d", &row, &col);}
	ginfo->score = SC_INVALID;
	ginfo->id = ID0;
	SET(ginfo->x, ginfo->y, ID1);
}

int main(){
	init_maps();
#if 1
    round_init0(&ginfo);
    while (1) {
//		MSG("SET(%d, %d, ID0);\n", ginfo.x, ginfo.y);
        printf("%d %d\n", ginfo.y, ginfo.x);
		SET(ginfo.x, ginfo.y, ID0);
        round_init(&ginfo);
        get_res(&ginfo, ID0);
    }
#else
    get_res(&ginfo, ID0);
    printf("%d %d\n", ginfo.y, ginfo.x);
#endif
}

int get_res(ginfo_t * ginfo, int id){
	int bx, by, len, cnt = 0;
	int x, y, res_x=-1, res_y=-1;
	int high_score = SC_INVALID, tmp_score;
	UPDATE_FIELD_ALL();
	if(GET_STATE(FIELD_ALL) == DRAW_FULL) return SC_ZERO;
	else if(GET_STATE(FIELD_ALL) == id) return SC_WIN;
	else if(GET_STATE(FIELD_ALL) == OP_ID(id)) return -SC_WIN;
	else if(ginfo->cal_level > LEV_LIMIT){
		int i, res = 0;
		for(i=0;i<9;i++){
			if(GET_STATE(i)==id){ res += 100*ginfo->cal_level; }
			if(GET_STATE(i)==OP_ID(id)){ res -= 100*ginfo->cal_level; }
		}
		return res;
	}
	ginfo->cal_level++;
	if(GET_STATE_XY((ginfo->x%3)*3, (ginfo->y%3)*3) != UNKNOWN){ bx=by=0; len=9;}
	else{bx = (ginfo->x%3)*3; by = (ginfo->y%3)*3; len = 3; }
//	if(ginfo->cal_level<=1){MSG("st:%d (%d,%d)\n", GET_STATE_XY(ginfo->x, ginfo->y), bx, by);}
	for(y=by;y<by+len;y++) for(x=bx;x<bx+len;x++){
		if(IS_VALID(x, y)){
			if(++cnt > FIELD_ALL){break;}
//			if(ginfo->cal_level<=1){MSG("%d (%d,%d)\n", ginfo->cal_level, bx+x, by+y);}
			SET(x, y, id);
			ginfo->x = x; ginfo->y = y;
			tmp_score = -get_res(ginfo, OP_ID(id));
			tmp_score += ginfo->cal_level;
//			if(ginfo->cal_level<=1){MSG("sc %d %d,%d (%d,%d)\n", ginfo->cal_level, high_score, tmp_score, res_x, res_y);}
			if(high_score < tmp_score){
				high_score = tmp_score;
				res_x = x; res_y = y;
			}
			CLEAR(x, y);
		}
	}
	ginfo->cal_level--;
	ginfo->x = res_x; ginfo->y = res_y; 
	return high_score;
}
